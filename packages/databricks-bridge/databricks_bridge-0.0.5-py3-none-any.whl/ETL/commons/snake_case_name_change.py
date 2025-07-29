import re

def camel_to_snake_case(camel_string):
    """
    Convert a camelCase string to snake_case format.
    
    Parameters:
        camel_string (str): The camelCase string to be converted.
        
    Returns:
        str: The string converted to snake_case.
    """
    snake_string = re.sub(r'(?<!^)(?=[A-Z])|(?<=[a-z])(?=[A-Z])', '_', camel_string)
    snake_string = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', snake_string).lower() # Convert to lowercase
    without_spaces_regex = re.sub(r"\s+", "", snake_string) # remove spaces

    return without_spaces_regex


def identify_case(spark, table_name):
    """
    Takes the name of a Databricks table as input and identifies 
    whether the column names in the table are in camelCase or snake_case format.
    
    Parameters:
    - table_name (str): The name 
    of the Databricks table.
    
    Returns:
    - dict: A list that contains all snake case column names and another that contains all camel case columns 
    """
    # Read the table into a DataFrame
    df = spark.table(table_name)
    
    columns = df.columns # Get the column names
    # Define regular expressions for camel case and snake case
    camel_case_pattern = re.compile(r'^[a-z]+(?:[A-Z][a-z]*)*$')
    snake_case_pattern = re.compile(r'^[a-z]+(?:_[a-z]+)*$')
    case_dict = {} # Dictionary to store column name and case

    # Identify the case for each column
    camel_case_cols = []
    snake_case_cols = []
    unknown_cols = []
    for col in columns:
        if camel_case_pattern.match(col):
            case_dict[col] = 'camelCase' # Checking the case

            index=[x for x,y in enumerate(list(col)) if(y.isupper())] # Defining the checks
            camel_=[]
            temp=0
            for m in index:
                camel_.append(col[temp:m])
                temp=m
            if(len(index)>0):
                camel_.append(col[index[-1]::])
                print('The individual camel case words are', camel_) 
            else:
                camel_.append(col)
                print('The given string is not camel case')

            if len(camel_) > 1:
                camel_case_cols.append(col)

        elif snake_case_pattern.match(col):
            case_dict[col] = 'snake_case'
            snake_case_cols.append(col)
        else:
            case_dict[col] = 'Unknown'
            unknown_cols.append(col)

    return camel_case_cols, snake_case_cols, unknown_cols

# Example Usage
# from ETL.commons.start_spark_session import get_or_create_spark_session
# import re
# table_name = 'client_holdings.history'
# env=locals()
# spark, sc, spark_ui_url = get_or_create_spark_session(env)
# camel_case_cols, snake_case_cols = identify_case(spark, table_name)