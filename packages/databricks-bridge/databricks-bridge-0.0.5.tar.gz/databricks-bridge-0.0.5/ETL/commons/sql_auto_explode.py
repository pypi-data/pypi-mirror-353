import json
from pyspark.sql.types import StructType


class SQLAutoExplode:
    def __init__(self, src_table_name: str, src_table_schema: StructType):
        self.src_table_name = src_table_name
        self.schema_dict = json.loads(src_table_schema.json())
        self.field_pointers, self.array_fields = self.retrieve_all_field_pointers()
        self.field_pointers.sort()
        self.array_fields.sort()
        self.splits = self.split_into_levels()
        self.exploded_cols = self.add_explode_to_array_cols()
        self.aliased_pointers = self.fix_pointers_and_aliases()
        self.select_query = self.build_select_query()

    def retrieve_all_field_pointers(self):
        def _recur(fields_schema: list, parent_field: str, field_pointer: list = [], array_fields: list = []):
            for field_dict in fields_schema:
                new_parent_field = f"{parent_field}.{field_dict['name']}" if parent_field else field_dict['name']
                if isinstance(field_dict["type"], str):
                    # nested_field = f"{parent_field}.{field_dict['name']} {parent_field}_{field_dict['name']}" if parent_field else field_dict['name']
                    nested_field = f"{parent_field}.{field_dict['name']}" if parent_field else field_dict['name']
                    field_pointer.append(nested_field)
                elif isinstance(field_dict["type"], dict):
                    if "fields" in field_dict["type"].keys():
                        _ret = _recur(fields_schema=field_dict["type"]["fields"], parent_field=new_parent_field,
                                      field_pointer=field_pointer, array_fields=array_fields)
                        field_pointer = _ret[0]
                        array_fields = _ret[1]
                    elif "elementType" in field_dict["type"].keys():
                        array_fields.append(new_parent_field)
                        _ret = _recur(fields_schema=field_dict["type"]["elementType"]["fields"],
                                      parent_field=new_parent_field, field_pointer=field_pointer, array_fields=array_fields)
                        field_pointer = _ret[0]
                        array_fields = _ret[1]
                    else:
                        print(f"not sure what is in here\n{field_dict}")
                else:
                    print(f"not sure what is in here either\n{field_dict}")

            return field_pointer, array_fields

        return _recur(fields_schema=self.schema_dict["fields"], parent_field="")

    def split_into_levels(self):
        max_depth = max([col.count('.') for col in self.field_pointers]) + 1
        all_lvls = []
        for i in range(max_depth):
            lvl = list(set(['.'.join(col.split(".")[:i + 1]) for col in self.field_pointers]))
            prev_lvl = [] if i == 0 else list(set(['.'.join(col.split(".")[:i]) for col in self.field_pointers]))
            new_lvl = []
            for el in lvl:
                if not prev_lvl:
                    new_lvl.append(el)
                else:
                    for prev_lvl_el in prev_lvl:
                        if prev_lvl_el == el[:len(prev_lvl_el)]:
                            new_el = prev_lvl_el.replace('.', '_') + '.' + el.split('.')[-1] if len(el) > len(
                                prev_lvl_el) else prev_lvl_el.replace('.', '_')
                            new_lvl.append(new_el)
                            break
            new_lvl.sort()
            all_lvls.append(new_lvl)

        all_lvls.sort()
        return all_lvls

    def add_explode_to_array_cols(self):
        explode_cols = []
        for split in self.splits:
            lvl_arr_cols = [_col for _col in split if _col.replace('_', '.') in self.array_fields]
            if len(lvl_arr_cols) == 1:
                explode_exp = [f"{el} {el.replace('.', '_')}" if el != lvl_arr_cols[
                    0] else f"explode_outer({el}) {el.replace('.', '_')}" for el in split]
                explode_cols.append(explode_exp)
            elif len(lvl_arr_cols) > 1:
                for arr_col in lvl_arr_cols:
                    explode_exp = [
                        f"{el} {el.replace('.', '_')}" if el != arr_col else f"explode_outer({el}) {el.replace('.', '_')}"
                        for el in split]
                    explode_cols.append(explode_exp)
            else:
                explode_exp = [f"{el} {el.replace('.', '_')}" for el in split]
                explode_cols.append(explode_exp)

        return explode_cols

    def fix_pointers_and_aliases(self):
        aliased_cols = []
        for lvl_cols in self.exploded_cols:
            if not aliased_cols:
                aliased_cols.append(lvl_cols)
            else:
                aliases = [_col.split(" ")[-1] for _col in aliased_cols[-1]]
                pointers = [_col.split(" ")[0].replace("explode_outer(", "").replace(")", "") for _col in
                            aliased_cols[-1]]
                lvl_aliases = [_col.split(" ")[-1] for _col in lvl_cols]
                lvl_pointers = [_col.split(" ")[0].replace("explode_outer(", "").replace(")", "") for _col in lvl_cols]
                new_lvl_cols = []
                for i in range(len(lvl_cols)):
                    if lvl_pointers[i] in pointers:
                        new_lvl_cols.append(lvl_cols[i].replace(lvl_pointers[i], lvl_aliases[i]))
                    else:
                        new_lvl_cols.append(lvl_cols[i])

                aliased_cols.append(new_lvl_cols)

        return aliased_cols

    def build_select_query(self):
        lvl_sql = self.src_table_name
        for i in range(len(self.aliased_pointers)):
            tab_spacer = len(self.aliased_pointers) - i
            if i == 0:
                lvl_sql = "select " + ", ".join(self.aliased_pointers[i]) + f" from {lvl_sql}"
            else:
                lvl_sql = "select " + ", ".join(self.aliased_pointers[i]) + " from (\n" + "\t"*tab_spacer + lvl_sql + "\n" + "\t"*(tab_spacer-1) + ")"

        return lvl_sql


def null_if_not_exists(select_str: str, col_name: str):
    return col_name if col_name in select_str else 'null'
