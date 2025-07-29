import requests
import pandas as pd
from .util import get_response_json_with_check
from ..enums import PenetrateType, PositionField

default_fields = [
    'assetCategory',
    'date',
    'assetName',
    'assetCode',
    'securityType',
    'exchangeCd',
    'netPrice',
    'aiRate',
    'chg',
    'amount',
    'marketValueLocal',
    'weight',
    'dailyProfitValueLocal',
    'dailyProfitRate',
    'floatingProfitValueLocal',
    'floatingProfitRate',
    'cumulativeProfitValueLocal',
    'cumulativeProfitRate',
    'totalBuyCostLocal',
    'realizedAiLocal',
    'realizedProfitValueLocal',
    'channel',
    'positionTime'
]

field_enum_mapping = {
    PositionField.CLASS: 'assetCategory',
    PositionField.DATE: 'date',
    PositionField.ASSET_NAME: 'assetName',
    PositionField.ASSET_CODE: 'assetCode',
    PositionField.SECURITY_TYPE: 'securityType',
    PositionField.TRADING_MARKET: 'exchangeCd',
    PositionField.CURRENT_CLEAN_PRICE: 'netPrice',
    PositionField.ACCRUED_INTEREST: 'aiRate',
    PositionField.PRICE_CHANGE: 'chg',
    PositionField.POSITION_QUANTITY: 'amount',
    PositionField.POSITION_MARKET_VALUE: 'marketValueLocal',
    PositionField.POSITION_WEIGHT_NET_ASSETS: 'weight',
    PositionField.DAILY_PROFIT_LOSS: 'dailyProfitValueLocal',
    PositionField.DAILY_PROFIT_LOSS_RATE: 'dailyProfitRate',
    PositionField.FLOATING_PROFIT_LOSS: 'floatingProfitValueLocal',
    PositionField.FLOATING_PROFIT_LOSS_RATE: 'floatingProfitRate',
    PositionField.CUMULATIVE_PROFIT_LOSS: 'cumulativeProfitValueLocal',
    PositionField.CUMULATIVE_PROFIT_LOSS_RATE: 'cumulativeProfitRate',
    PositionField.POSITION_COST: 'totalBuyCostLocal',
    PositionField.INTEREST_INCOME: 'realizedAiLocal',
    PositionField.REALIZED_PROFIT_LOSS: 'realizedProfitValueLocal',
    PositionField.MATURITY_DATE: 'dueDate',
    PositionField.TRADING_CHANNEL: 'channel',
    PositionField.POSITION_DIRECTION: 'direction',
    PositionField.LATEST_PRICE: 'price',
    PositionField.POSITION_WEIGHT_TOTAL_ASSETS: 'weightTotal',
    PositionField.POSITION_WEIGHT_TOTAL_COST: 'weightCost',
    PositionField.COST_PRICE: 'buyCost',
    PositionField.AMORTIZED_COST: 'cost',
    PositionField.VALUATION_EXCHANGE_RATE: 'fxRate',
    PositionField.MARKET_QUOTATION_TIME: 'positionTime',
    PositionField.POSITION_BUILDING_DATE: 'holdDate',
    PositionField.ISSUING_ENTITY: 'partyFullName',
    PositionField.REMAINING_MATURITY: 'yearToMaturity',
    PositionField.BOND_RATING_AGENCY: 'nominalRatingInst',
    PositionField.BOND_RATING: 'nominalRating',
    PositionField.MARGIN_REQUIREMENT: 'margin',
    PositionField.CITY: 'city',
    PositionField.PROVINCE: 'province',
    PositionField.ISSUER_RATING_YY: 'instRatingYY',
    PositionField.ISSUER_RATING_DATE: 'instRatingDate',
    PositionField.ISSUER_RATING: 'instRating',
    PositionField.BOND_RATING_DATE: 'nominalRatingDate',
    PositionField.ISSUER_RATING_AGENCY: 'instRatingInst'
}

field_mapping = {
    'assetCategory': 'class',
    'date': 'date',
    'assetName': 'asset_name',
    'assetCode': 'asset_code',
    'securityType': 'security_type',
    'exchangeCd': 'trading_market',
    'netPrice': 'current_clean_price',
    'aiRate': 'accrued_interest',
    'chg': 'price_change',
    'amount': 'position_quantity',
    'marketValueLocal': 'position_market_value',
    'weight': 'position_weight_(net_assets)',
    'dailyProfitValueLocal': 'daily_profit_loss',
    'dailyProfitRate': 'daily_profit_loss_rate',
    'floatingProfitValueLocal': 'floating_profit_loss',
    'floatingProfitRate': 'floating_profit_loss_rate',
    'cumulativeProfitValueLocal': 'cumulative_profit_loss',
    'cumulativeProfitRate': 'cumulative_profit_loss_rate',
    'totalBuyCostLocal': 'position_cost',
    'realizedAiLocal': 'interest_income',
    'realizedProfitValueLocal': 'realized_profit_loss',
    'dueDate': 'maturity_date',
    'channel': 'trading_channel',
    'direction': 'position_direction',
    'price': 'latest_price',
    'weightTotal': 'position_weight_(total_assets)',
    'weightCost': 'position_weight_(total_cost)',
    'buyCost': 'cost_price',
    'cost': 'amortized_cost',
    'fxRate': 'valuation_exchange_rate',
    'positionTime': 'market_quotation_time',
    'holdDate': 'position_building_date',
    'partyFullName': 'issuing_entity',
    'yearToMaturity': 'remaining_maturity',
    'nominalRatingInst': 'bond_rating_agency',
    'nominalRating': 'bond_rating',
    'margin': 'margin_requirement',
    'city': 'city',
    'province': 'province',
    'instRatingYY': 'issuer_rating_(YY)',
    'instRatingDate': 'issuer_rating_date',
    'instRating': 'issuer_rating',
    'nominalRatingDate': 'bond_rating_date',
    'instRatingInst': 'issuer_rating_agency'
}


def get_post_investment_product_holdings(client,
                                         post_investment_product_id,
                                         start_date=None,
                                         end_date=None,
                                         date=None,
                                         asset_class="交易属性",
                                         penetrate_type=PenetrateType.NO_PENETRATE,
                                         level=1,
                                         fields=[]):

    if date:
        start_date = date
        end_date = date
    elif not start_date or not end_date:
        raise ValueError("start_date and end_date are required")

    url = f"{client.base_url}/lib/portfolio/v1/position"
    data = {
        'accountCode': post_investment_product_id,
        'startDate': start_date,
        'endDate': end_date,
        'penetrateWay': penetrate_type.name if penetrate_type else PenetrateType.NO_PENETRATE,
        'level': level,
        'assetCategoryName': asset_class
    }
    headers = client.get_headers()
    try:
        response = requests.post(url, headers=headers, json=data)
        r = get_response_json_with_check(response)

        if not fields:
            fields = default_fields
        else:
            fields = default_fields + [
                field_enum_mapping[field]
                for field in fields
                if field in field_enum_mapping
                and field_enum_mapping[field] in field_mapping
                and field_enum_mapping[field] not in default_fields
            ]
        rows = []
        for item in r.get('list'):
            row = {}
            for field in fields:
                row[field_mapping[field]] = item.get(field, None)
            rows.append(row)
        df = pd.DataFrame(rows)
        return df
    except Exception as e:
        raise e
