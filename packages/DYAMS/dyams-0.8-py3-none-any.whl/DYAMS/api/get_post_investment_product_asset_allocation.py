import requests
import pandas as pd
from .util import get_response_json_with_check
from ..enums import PenetrateType, WeightType

field_mapping = {
    'date': 'date',
    'assetCategory': 'asset_type',
    'weight': 'weight',
    'marketValue': 'position_market_value'
}


def get_post_investment_product_asset_allocation(client,
                                                 post_investment_product_id,
                                                 start_date=None,
                                                 end_date=None,
                                                 date=None,
                                                 asset_class="交易属性",
                                                 penetrate_type=PenetrateType.NO_PENETRATE,
                                                 level=1,
                                                 weight_types=WeightType.TOTAL_FILTERED,
                                                 asset_sceening=[]):

    if date:
        start_date = date
        end_date = date
    elif not start_date or not end_date:
        raise ValueError("start_date and end_date are required")

    url = f"{client.base_url}/lib/portfolio/v1/positionDistribution"
    data = {
        'accountCode': post_investment_product_id,
        'startDate': start_date,
        'endDate': end_date,
        'penetrateWay': penetrate_type.name if penetrate_type else PenetrateType.NO_PENETRATE,
        'level': level,
        'assetCategoryName': asset_class,
        'ratioAssetType': weight_types.name if weight_types else WeightType.TOTAL_FILTERED,
        'securityTypes': [security_type.name for security_type in asset_sceening]
    }
    headers = client.get_headers()
    try:
        response = requests.post(url, headers=headers, json=data)
        r = get_response_json_with_check(response)

        rows = []
        for item in r.get('list'):
            row = {}
            for api_field, our_field in field_mapping.items():
                row[our_field] = item.get(api_field, None)
            rows.append(row)

        df = pd.DataFrame(rows)
        return df
    except Exception as e:
        raise e
