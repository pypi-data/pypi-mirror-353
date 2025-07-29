import os
from google.oauth2.service_account import Credentials
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)


def sample_run_report(property_id="YOUR-GA4-PROPERTY-ID"):
    property_id = "344436016"

    # Using a default constructor instructs the client to use the credentials
    # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
    base_path = "/dbfs/FileStore" if os.environ.get('ISDATABRICKS',
                                                    'local') == "TRUE" else "/Users/muhammad-saeedfalowo/Documents/codebase/lakehouse/ETL/scripts/google_analytics"
    token_path = f"{base_path}/ga4apidataretrie_1739871769222_f61604b3f475.json"
    # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = token_path
    # client = BetaAnalyticsDataClient()
    creds = Credentials.from_service_account_file(token_path)
    client = BetaAnalyticsDataClient(credentials=creds)

    # dimension_fields = [
    #     "sessionGoogleAdsCampaignId", "sessionGoogleAdsCampaignName", "sessionGoogleAdsCampaignType",
    #     "sessionGoogleAdsAdGroupId", "sessionGoogleAdsAdGroupName", "sessionGoogleAdsKeyword"
    # ]
    #
    # metrics_fields = [
    #     [
    #         "advertiserAdClicks", "publisherAdClicks", "advertiserAdCost", "advertiserAdCostPerClick",
    #         "advertiserAdImpressions", "publisherAdImpressions", "advertiserAdCostPerKeyEvent"
    #     ]
    # ]

    dimension_fields = [
        "deviceCategory", "newVsReturning", "sessionSource", "sessionSourceMedium", "sessionSourcePlatform",
        "sessionPrimaryChannelGroup", "landingPage", "eventName", "sessionGoogleAdsCampaignId"
    ]
    metrics_fields = [
        "averageSessionDuration", "bounceRate", "engagedSessions", "eventsPerSession", "screenPageViewsPerSession",
        "sessionKeyEventRate", "sessions", "newUsers", "screenPageViews", "screenPageViewsPerUser"
    ]

    def _get_response(_dimension_fields, _metrics_fields):
        dimensions = [Dimension(name=el) for el in _dimension_fields]
        metrics = [Metric(name=el) for el in _metrics_fields]

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=dimensions,
            metrics=metrics,
            # date_ranges=[DateRange(start_date="2025-01-31", end_date="today")],
            date_ranges=[DateRange(start_date="2025-03-08", end_date="2025-03-08")],
        )
        response = client.run_report(request)

        return response

    response = _get_response(dimension_fields, metrics_fields)

    print("Report result:")
    print(response)

    # for i in range(len(metrics_fields)):
        # dimensions = [Dimension(name=el) for el in dimension_fields]
        # metrics = [Metric(name=el) for el in metrics_fields[i]]
        #
        # request = RunReportRequest(
        #     property=f"properties/{property_id}",
        #     dimensions=dimensions,
        #     metrics=metrics,
        #     # date_ranges=[DateRange(start_date="2025-01-31", end_date="today")],
        #     date_ranges=[DateRange(start_date="2025-03-08", end_date="2025-03-08")],
        # )
        # response = _get_response(_dimension_fields, _metrics_fields)

        # print("Report result:")
        # print(response)
        # breakpoint()

        # data = []
        # for row in response.rows:
        #     dimensions_data = {response.dimension_headers[i].name: row.dimension_values[i].value for i in range(len(row.dimension_values))}
        #     metrics_data = {response.metric_headers[i].name: row.metric_values[i].value for i in range(len(row.metric_values))}
        #     data.append({**dimensions_data, **metrics_data})
        #
        # print(data)
        # break


if __name__ == "__main__":
    sample_run_report()

# REF: https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart-client-libraries
# REF: https://www.lupagedigital.com/blog/google-analytics-api-python/
