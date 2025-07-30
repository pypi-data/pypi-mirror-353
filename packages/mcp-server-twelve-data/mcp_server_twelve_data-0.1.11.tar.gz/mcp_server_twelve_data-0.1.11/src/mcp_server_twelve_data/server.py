import logging
from typing import Type, TypeVar, Literal
import httpx
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

from mcp_server_twelve_data.request_models import GetTimeSeriesRequest, GetPriceRequest, GetEodRequest, GetQuoteRequest, \
    GetMarketStateRequest, GetEarningsRequest, GetTimeSeriesRsiRequest, GetStocksRequest, GetTimeSeriesMacdRequest, \
    GetExchangeRateRequest, GetProfileRequest, GetStatisticsRequest, GetSymbolSearchRequest, GetTimeSeriesAvgRequest, \
    GetTimeSeriesSmaRequest, GetLogoRequest, GetApiUsageRequest, GetTimeSeriesEmaRequest, GetExchangeScheduleRequest, \
    GetTimeSeriesAtrRequest, GetMutualFundsWorldSummaryRequest, GetMutualFundsWorldRequest, GetTimeSeriesVwapRequest, \
    GetTimeSeriesCrsiRequest, GetEarliestTimestampRequest, GetPriceTargetRequest, GetIncomeStatementRequest, \
    GetDividendsRequest, GetCashFlowRequest, GetBalanceSheetRequest, GetTimeSeriesBBandsRequest, \
    GetRecommendationsRequest, GetCurrencyConversionRequest, GetEtfRequest, GetSplitsRequest, \
    GetEarningsEstimateRequest, GetTimeSeriesStochRequest, GetRevenueEstimateRequest, \
    GetAnalystRatingsUsEquitiesRequest, GetInsiderTransactionsRequest, GetGrowthEstimatesRequest, \
    GetInstitutionalHoldersRequest, GetTimeSeriesSarRequest, GetTimeSeriesHtTrendlineRequest, GetEpsRevisionsRequest, \
    GetEpsTrendRequest, GetKeyExecutivesRequest, GetAnalystRatingsLightRequest, GetTimeSeriesWmaRequest, \
    GetCrossListingsRequest
from mcp_server_twelve_data.response_models import GetTimeSeries200Response, GetPrice200Response, GetEod200Response, \
    GetQuote200Response, GetMarketState200Response, GetEarnings200Response, GetTimeSeriesRsi200Response, \
    GetStocks200Response, GetTimeSeriesMacd200Response, GetExchangeRate200Response, GetProfile200Response, \
    GetStatistics200Response, GetSymbolSearch200Response, GetTimeSeriesAvg200Response, GetTimeSeriesSma200Response, \
    GetLogo200Response, GetApiUsage200Response, GetTimeSeriesEma200Response, GetExchangeSchedule200Response, \
    GetTimeSeriesAtr200Response, GetMutualFundsWorldSummary200Response, GetMutualFundsWorld200Response, \
    GetTimeSeriesVwap200Response, GetTimeSeriesCrsi200Response, GetEarliestTimestamp200Response, \
    GetPriceTarget200Response, GetIncomeStatement200Response, GetDividends200Response, GetCashFlow200Response, \
    GetBalanceSheet200Response, GetTimeSeriesBBands200Response, GetRecommendations200Response, \
    GetCurrencyConversion200Response, GetEtf200Response, GetSplits200Response, GetEarningsEstimate200Response, \
    GetTimeSeriesStoch200Response, GetRevenueEstimate200Response, GetAnalystRatingsUsEquities200Response, \
    GetInsiderTransactions200Response, GetGrowthEstimates200Response, GetInstitutionalHolders200Response, \
    GetTimeSeriesSar200Response, GetTimeSeriesHtTrendline200Response, GetEpsRevisions200Response, \
    GetEpsTrend200Response, GetKeyExecutives200Response, GetAnalystRatingsLight200Response, GetTimeSeriesWma200Response, \
    GetCrossListings200Response


def serve(
    api_base: str,
    transport: Literal["stdio", "sse", "streamable-http"],
    apikey: str,
) -> None:
    logger = logging.getLogger(__name__)

    server = FastMCP(
        "mcp-twelve-data",
        host="0.0.0.0",
        port="8000",
    )

    P = TypeVar('P', bound=BaseModel)
    R = TypeVar('R', bound=BaseModel)

    async def _call_endpoint(
        endpoint: str,
        params: P,
        response_model: Type[R]
    ) -> R:
        if apikey:
            params.apikey = apikey

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{api_base}/{endpoint}",
                params=params.model_dump(exclude_none=True)
            )
            resp.raise_for_status()
            return response_model.model_validate(resp.json())

    @server.tool(name="GetTimeSeries", description="This API call returns meta and time series for the requested instrument. Metaobject consists of general information about the requested symbol. Time series is the array of objects ordered by time descending with Open, High, Low, Close prices. Non-currency instruments also include volume information.")
    async def GetTimeSeries(params: GetTimeSeriesRequest) -> GetTimeSeries200Response:
        return await _call_endpoint("time_series", params, GetTimeSeries200Response)

    @server.tool(name="GetPrice", description="This endpoint is a lightweight method that allows retrieving only the real-time price of the selected instrument.")
    async def GetPrice(params: GetPriceRequest) -> GetPrice200Response:
        return await _call_endpoint("price", params, GetPrice200Response)

    @server.tool(name="GetEod", description="This endpoint returns the latest End of Day (EOD) price of an instrument.")
    async def GetEod(params: GetEodRequest) -> GetEod200Response:
        return await _call_endpoint("eod", params, GetEod200Response)

    @server.tool(name="GetQuote", description="Quote endpoint is an efficient method to retrieve the latest quote of the selected instrument.")
    async def GetQuote(params: GetQuoteRequest) -> GetQuote200Response:
        return await _call_endpoint("quote", params, GetQuote200Response)

    @server.tool(name="GetMarketState", description="Check the state of all available exchanges, time to open, and time to close. Returns all available stock exchanges by default.")
    async def GetMarketState(params: GetMarketStateRequest) -> GetMarketState200Response:
        return await _call_endpoint("market_state", params, GetMarketState200Response)

    @server.tool(name="GetEarnings", description="This API call returns earnings data for a given company, including EPS estimate and EPS actual. Earnings are available for complete company history.")
    async def GetEarnings(params: GetEarningsRequest) -> GetEarnings200Response:
        return await _call_endpoint("earnings", params, GetEarnings200Response)

    @server.tool(name="GetTimeSeriesRsi", description="The Relative Strength Index (RSI) is a momentum oscillator that measures the speed and change of price movements, helping traders identify potential overbought or oversold conditions and trend reversals.")
    async def GetTimeSeriesRsi(params: GetTimeSeriesRsiRequest) -> GetTimeSeriesRsi200Response:
        return await _call_endpoint("rsi", params, GetTimeSeriesRsi200Response)

    @server.tool(name="GetStocks", description="This API call returns an array of symbols available at Twelve Data API. This list is updated daily.")
    async def GetStocks(params: GetStocksRequest) -> GetStocks200Response:
        return await _call_endpoint("stocks", params, GetStocks200Response)

    @server.tool(name="GetTimeSeriesMacd", description="The Moving Average Convergence Divergence (MACD) is a momentum indicator that measures the difference between two moving averages, with a signal line used to identify potential trend reversals and trading opportunities.")
    async def GetTimeSeriesMacd(params: GetTimeSeriesMacdRequest) -> GetTimeSeriesMacd200Response:
        return await _call_endpoint("macd", params, GetTimeSeriesMacd200Response)

    @server.tool(name="GetExchangeRate", description="This API call returns real-time exchange rate for currency pair. Works with forex and cryptocurrency.")
    async def GetExchangeRate(params: GetExchangeRateRequest) -> GetExchangeRate200Response:
        return await _call_endpoint("exchange_rate", params, GetExchangeRate200Response)

    @server.tool(name="GetProfile", description="Returns general information about the company.")
    async def GetProfile(params: GetProfileRequest) -> GetProfile200Response:
        return await _call_endpoint("profile", params, GetProfile200Response)

    @server.tool(name="GetStatistics",
                 description="Returns current overview of companys main statistics including valuation metrics and financials.")
    async def GetStatistics(params: GetStatisticsRequest) -> GetStatistics200Response:
        return await _call_endpoint("statistics", params, GetStatistics200Response)

    @server.tool(name="GetSymbolSearch", description="This method helps to find the best matching symbol. It can be used as the base for custom lookups. The response is returned in descending order, with the most relevant instrument at the beginning.")
    async def GetSymbolSearch(params: GetSymbolSearchRequest) -> GetSymbolSearch200Response:
        return await _call_endpoint("symbol_search", params, GetSymbolSearch200Response)

    @server.tool(name="GetTimeSeriesAvg", description="The Average (AVG) indicator calculates the arithmetic mean of a data series over a specified period, often used to smooth out data fluctuations.")
    async def GetTimeSeriesAvg(params: GetTimeSeriesAvgRequest) -> GetTimeSeriesAvg200Response:
        return await _call_endpoint("avg", params, GetTimeSeriesAvg200Response)

    @server.tool(name="GetTimeSeriesSma",
                 description="The Simple Moving Average (SMA) is a smoothing indicator that calculates the average price of a security over a specified period, helping traders identify trends and potential support or resistance levels.")
    async def GetTimeSeriesSma(params: GetTimeSeriesSmaRequest) -> GetTimeSeriesSma200Response:
        return await _call_endpoint("sma", params, GetTimeSeriesSma200Response)

    @server.tool(name="GetLogo", description="Returns a logo of company, cryptocurrency, or forex pair.")
    async def GetLogo(params: GetLogoRequest) -> GetLogo200Response:
        return await _call_endpoint("logo", params, GetLogo200Response)

    @server.tool(name="GetApiUsage", description="This endpoint will provide information on the current usage of Twelve Data API.")
    async def GetApiUsage(params: GetApiUsageRequest) -> GetApiUsage200Response:
        return await _call_endpoint("api_usage", params, GetApiUsage200Response)

    @server.tool(name="GetTimeSeriesEma", description="The Exponential Moving Average (EMA) is a weighted moving average that gives more importance to recent price data, making it more responsive to new information and helping traders identify trends and potential entry or exit points.")
    async def GetTimeSeriesEma(params: GetTimeSeriesEmaRequest) -> GetTimeSeriesEma200Response:
        return await _call_endpoint("ema", params, GetTimeSeriesEma200Response)

    @server.tool(name="GetExchangeSchedule", description="This API call return exchanges details and trading hours.")
    async def GetExchangeSchedule(params: GetExchangeScheduleRequest) -> GetExchangeSchedule200Response:
        return await _call_endpoint("exchange_schedule", params, GetExchangeSchedule200Response)

    @server.tool(name="GetTimeSeriesAtr", description="The Average True Range (ATR) is a volatility indicator that measures the average range of price movement over a specified period, helping traders assess market volatility.")
    async def GetTimeSeriesAtr(params: GetTimeSeriesAtrRequest) -> GetTimeSeriesAtr200Response:
        return await _call_endpoint("atr", params, GetTimeSeriesAtr200Response)

    @server.tool(name="GetMutualFundsWorldSummary", description="This API request returns a brief summary of a mutual fund.")
    async def GetMutualFundsWorldSummary(params: GetMutualFundsWorldSummaryRequest) -> GetMutualFundsWorldSummary200Response:
        return await _call_endpoint("mutual_funds/world/summary", params, GetMutualFundsWorldSummary200Response)

    @server.tool(name="GetMutualFundsWorld", description="This API request returns a complete breakdown of a mutual fund, including summary, performance, risk, ratings, composition, purchase_info, and sustainability.")
    async def GetMutualFundsWorld(params: GetMutualFundsWorldRequest) -> GetMutualFundsWorld200Response:
        return await _call_endpoint("mutual_funds/world", params, GetMutualFundsWorld200Response)

    @server.tool(name="GetTimeSeriesVwap", description="The Volume Weighted Average Price (VWAP) indicator offers an insightful measure of the average trading price weighted by volume, commonly used for trading analysis and execution evaluation.")
    async def GetTimeSeriesVwap(params: GetTimeSeriesVwapRequest) -> GetTimeSeriesVwap200Response:
        return await _call_endpoint("vwap", params, GetTimeSeriesVwap200Response)

    @server.tool(name="GetTimeSeriesCrsi", description="The Connors RSI is a composite indicator combining the Relative Strength Index (RSI), the Rate of Change (ROC), and the Up/Down Length, providing a more comprehensive view of momentum and potential trend reversals.")
    async def GetTimeSeriesCrsi(params: GetTimeSeriesCrsiRequest) -> GetTimeSeriesCrsi200Response:
        return await _call_endpoint("crsi", params, GetTimeSeriesCrsi200Response)

    @server.tool(name="GetEarliestTimestamp", description="This method returns the first available DateTime for a given instrument at the specific interval.")
    async def GetEarliestTimestamp(params: GetEarliestTimestampRequest) -> GetEarliestTimestamp200Response:
        return await _call_endpoint("earliest_timestamp", params, GetEarliestTimestamp200Response)

    @server.tool(name="GetPriceTarget", description="This API endpoint returns the analysts' projection of a security's future price.")
    async def GetPriceTarget(params: GetPriceTargetRequest) -> GetPriceTarget200Response:
        return await _call_endpoint("price_target", params, GetPriceTarget200Response)

    @server.tool(name="GetIncomeStatement", description="Returns complete income statement of a company and shows the companys revenues and expenses during a period (annual or quarter).")
    async def GetIncomeStatement(params: GetIncomeStatementRequest) -> GetIncomeStatement200Response:
        return await _call_endpoint("income_statement", params, GetIncomeStatement200Response)

    @server.tool(name="GetDividends", description="Returns the amount of dividends paid out for the last 10+ years.")
    async def GetDividends(params: GetDividendsRequest) -> GetDividends200Response:
        return await _call_endpoint("dividends", params, GetDividends200Response)

    @server.tool(name="GetCashFlow", description="Returns complete cash flow of a company showing the net amount of cash and cash equivalents being transferred into and out of business.")
    async def GetCashFlow(params: GetCashFlowRequest) -> GetCashFlow200Response:
        return await _call_endpoint("cash_flow", params, GetCashFlow200Response)

    @server.tool(name="GetBalanceSheet", description="Returns complete balance sheet of a company showing the summary of assets, liabilities, and shareholders equity.")
    async def GetBalanceSheet(params: GetBalanceSheetRequest) -> GetBalanceSheet200Response:
        return await _call_endpoint("balance_sheet", params, GetBalanceSheet200Response)

    @server.tool(name="GetTimeSeriesBBands", description="Bollinger Bands (BBANDS) are volatility bands placed above and below a moving average, measuring price volatility and helping traders identify potential overbought or oversold conditions.")
    async def GetTimeSeriesBBands(params: GetTimeSeriesBBandsRequest) -> GetTimeSeriesBBands200Response:
        return await _call_endpoint("bbands", params, GetTimeSeriesBBands200Response)

    @server.tool(name="GetRecommendations", description="This API endpoint returns the average of all analyst recommendations and classifies them as Strong Buy, Buy, Hold, or Sell. Also, it returns a recommendation score.")
    async def GetRecommendations(params: GetRecommendationsRequest) -> GetRecommendations200Response:
        return await _call_endpoint("recommendations", params, GetRecommendations200Response)

    @server.tool(name="GetCurrencyConversion", description="This API call returns real-time exchange rate and converted amount for currency pair. Works with forex and cryptocurrency.")
    async def GetCurrencyConversion(params: GetCurrencyConversionRequest) -> GetCurrencyConversion200Response:
        return await _call_endpoint("currency_conversion", params, GetCurrencyConversion200Response)

    @server.tool(name="GetEtf", description="This API call returns an array of ETFs available at Twelve Data API. This list is updated daily.")
    async def GetEtf(params: GetEtfRequest) -> GetEtf200Response:
        return await _call_endpoint("etfs", params, GetEtf200Response)

    @server.tool(name="GetSplits", description="Returns the date and the split factor of shares of the company for the last 10+ years.")
    async def GetSplits(params: GetSplitsRequest) -> GetSplits200Response:
        return await _call_endpoint("splits", params, GetSplits200Response)

    @server.tool(name="GetEarningsEstimate", description="This API endpoint returns analysts' estimate for a company's future quarterly and annual earnings per share (EPS).")
    async def GetEarningsEstimate(params: GetEarningsEstimateRequest) -> GetEarningsEstimate200Response:
        return await _call_endpoint("earnings_estimate", params, GetEarningsEstimate200Response)

    @server.tool(name="GetTimeSeriesStoch", description="The Stochastic Oscillator (STOCH) is a momentum indicator that compares a security's closing price to its price range over a specified period, helping traders identify potential overbought or oversold conditions and trend reversals.")
    async def GetTimeSeriesStoch(params: GetTimeSeriesStochRequest) -> GetTimeSeriesStoch200Response:
        return await _call_endpoint("stoch", params, GetTimeSeriesStoch200Response)

    @server.tool(name="GetRevenueEstimate", description="This API endpoint returns analysts' estimate for a company's future quarterly and annual sales (total revenue).")
    async def GetRevenueEstimate(params: GetRevenueEstimateRequest) -> GetRevenueEstimate200Response:
        return await _call_endpoint("revenue_estimate", params, GetRevenueEstimate200Response)

    @server.tool(name="GetAnalystRatingsUsEquities", description="This API endpoint returns complete information on ratings issued by analyst firms. Works only for US equities.")
    async def GetAnalystRatingsUsEquities(params: GetAnalystRatingsUsEquitiesRequest) -> GetAnalystRatingsUsEquities200Response:
        return await _call_endpoint("analyst_ratings/us_equities", params, GetAnalystRatingsUsEquities200Response)

    @server.tool(name="GetInsiderTransactions", description="Returns trading information performed by insiders.")
    async def GetInsiderTransactions(params: GetInsiderTransactionsRequest) -> GetInsiderTransactions200Response:
        return await _call_endpoint("insider_transactions", params, GetInsiderTransactions200Response)

    @server.tool(name="GetGrowthEstimates", description="This API endpoint returns consensus analyst estimates over the company's growth rates for various periods. Calculation averages projections of numerous analysts, taking arbitrary parameters, such as earnings per share, revenue, etc.")
    async def GetGrowthEstimates(params: GetGrowthEstimatesRequest) -> GetGrowthEstimates200Response:
        return await _call_endpoint("growth_estimates", params, GetGrowthEstimates200Response)

    @server.tool(name="GetInstitutionalHolders", description="Returns the amount of the companys available stock owned by institutions (pension funds, insurance companies, investment firms, private foundations, endowments, or other large entities that manage funds on behalf of others).")
    async def GetInstitutionalHolders(params: GetInstitutionalHoldersRequest) -> GetInstitutionalHolders200Response:
        return await _call_endpoint("institutional_holders", params, GetInstitutionalHolders200Response)

    @server.tool(name="GetTimeSeriesSar", description="The Parabolic SAR (SAR) is a trend-following indicator that calculates potential support and resistance levels based on a security's price and time, helping traders identify potential entry and exit points.")
    async def GetTimeSeriesSar(params: GetTimeSeriesSarRequest) -> GetTimeSeriesSar200Response:
        return await _call_endpoint("sar", params, GetTimeSeriesSar200Response)

    @server.tool(name="GetTimeSeriesHtTrendline", description="The Hilbert Transform Instantaneous Trendline (HT_TRENDLINE) is a smoothed moving average that follows the dominant market cycle, helping traders identify trends and potential entry or exit points.\n\nYou can read more about it in the Rocket Science for Traders book by John F. Ehlers.")
    async def GetTimeSeriesHtTrendline(params: GetTimeSeriesHtTrendlineRequest) -> GetTimeSeriesHtTrendline200Response:
        return await _call_endpoint("ht_trendline", params, GetTimeSeriesHtTrendline200Response)

    @server.tool(name="GetEpsRevisions", description="This API endpoint returns analysts revisions of a company's future quarterly and annual earnings per share (EPS) over the last week and month.")
    async def GetEpsRevisions(params: GetEpsRevisionsRequest) -> GetEpsRevisions200Response:
        return await _call_endpoint("eps_revisions", params, GetEpsRevisions200Response)

    @server.tool(name="GetEpsTrend", description="This API endpoint returns a breakdown of the estimated historical EPS changes at a given period.")
    async def GetEpsTrend(params: GetEpsTrendRequest) -> GetEpsTrend200Response:
        return await _call_endpoint("eps_trend", params, GetEpsTrend200Response)

    @server.tool(name="GetKeyExecutives", description="Returns key executive information for a specified symbol.")
    async def GetKeyExecutives(params: GetKeyExecutivesRequest) -> GetKeyExecutives200Response:
        return await _call_endpoint("key_executives", params, GetKeyExecutives200Response)

    @server.tool(name="GetAnalystRatingsLight", description="This API endpoint returns a lightweight version of ratings issued by analyst firms. Works for US and international markets.")
    async def GetAnalystRatingsLight(params: GetAnalystRatingsLightRequest) -> GetAnalystRatingsLight200Response:
        return await _call_endpoint("analyst_ratings/light", params, GetAnalystRatingsLight200Response)

    @server.tool(name="GetTimeSeriesWma", description="The Weighted Moving Average (WMA) is a smoothing indicator that calculates the average price of a security over a specified period, with more weight given to recent prices, providing a more responsive view of price action.")
    async def GetTimeSeriesWma(params: GetTimeSeriesWmaRequest) -> GetTimeSeriesWma200Response:
        return await _call_endpoint("wma", params, GetTimeSeriesWma200Response)

    @server.tool(name="GetCrossListings", description="This API call returns an array of cross listed symbols for a specified instrument. Cross listings are the same securities listed on different exchanges.")
    async def GetCrossListings(params: GetCrossListingsRequest) -> GetCrossListings200Response:
        return await _call_endpoint("cross_listings", params, GetCrossListings200Response)



    server.run(transport=transport)
