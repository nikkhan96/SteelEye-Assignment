import datetime as dt
import random
from typing import List, Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()


class TradeDetails(BaseModel):
    buySellIndicator: str = Field(
        description="A value of BUY for buys, SELL for sells."
    )
    price: float = Field(description="The price of the Trade.")
    quantity: int = Field(description="The amount of units traded.")


class Trade(BaseModel):
    asset_class: Optional[str] = Field(
        alias="assetClass",
        default=None,
        description="The asset class of the instrument traded. E.g. Bond, Equity, FX...etc",
    )
    counterparty: Optional[str] = Field(
        default=None,
        description="The counterparty the trade was executed with. May not always be available",
    )
    instrument_id: str = Field(
        alias="instrumentId", description="The ISIN/ID of the instrument traded. E.g. TSLA, AAPL, AMZN...etc"
    )
    instrument_name: str = Field(
        alias="instrumentName", description="The name of the instrument traded."
    )
    trade_date_time: dt.datetime = Field(
        alias="tradeDateTime", description="The date-time the Trade was executed"
    )
    trade_details: TradeDetails = Field(
        alias="tradeDetails", description="The details of the trade, i.e. price, quantity"
    )
    trade_id: str = Field(
        alias="tradeId", default=None, description="The unique ID of the trade"
    )
    trader: str = Field(description="The name of the Trader")


# Mock database layer and random trade data generation
mock_db = {}


def generate_trade_id():
    return str(random.randint(1, 100000))


def generate_random_trade():
    return Trade(
        asset_class=random.choice(["Equity", "Bond", "FX"]),
        counterparty=random.choice(["Counterparty A", "Counterparty B", None]),
        instrument_id="AAPL",
        instrument_name="Apple Inc.",
        trade_date_time=dt.datetime.now(),
        trade_details=TradeDetails(
            buySellIndicator=random.choice(["BUY", "SELL"]),
            price=random.uniform(100, 200),
            quantity=random.randint(1, 100),
        ),
        trade_id=generate_trade_id(),
        trader="John Doe",
    )


# Endpoint to retrieve a list of Trades with search, filter, pagination, and sorting capability
@app.get("/trades", response_model=List[Trade])
def get_trades(
    search: Optional[str] = Query(
        None, description="Search text to filter trades by counterparty, instrumentId, instrumentName, or trader"
    ),
    assetClass: Optional[str] = Query(None, description="Asset class of the trade."),
    start: Optional[dt.datetime] = Query(None, description="The minimum date for the tradeDateTime field."),
    end: Optional[dt.datetime] = Query(None, description="The maximum date for the tradeDateTime field."),
    minPrice: Optional[float] = Query(None, description="The minimum value for the tradeDetails.price field."),
    maxPrice: Optional[float] = Query(None, description="The maximum value for the tradeDetails.price field."),
    tradeType: Optional[str] = Query(None, description="The tradeDetails.buySellIndicator is a BUY or SELL."),
    page: Optional[int] = Query(1, gt=0, description="Page number for pagination"),
    size: Optional[int] = Query(10, gt=0, le=100, description="Number of trades per page"),
    sort: Optional[str] = Query(None, description="Sort trades by a specific field"),
):
    filtered_trades = []

    if search:
        search = search.lower()

    for trade in mock_db.values():
        if (
            (not assetClass or trade.asset_class == assetClass)
            and (not start or trade.trade_date_time >= start)
            and (not end or trade.trade_date_time <= end)
            and (not minPrice or trade.trade_details.price >= minPrice)
            and (not maxPrice or trade.trade_details.price <= maxPrice)
            and (not tradeType or trade.trade_details.buySellIndicator == tradeType)
            and (
                not search
                or search in trade.counterparty.lower()
                or search in trade.instrument_id.lower()
                or search in trade.instrument_name.lower()
                or search in trade.trader.lower()
            )
        ):
            filtered_trades.append(trade)

    # Sort trades if a sort field is provided
    if sort:
        try:
            filtered_trades.sort(key=lambda x: getattr(x, sort), reverse=False)
        except AttributeError:
            pass

    # Perform pagination
    start_index = (page - 1) * size
    end_index = start_index + size
    paged_trades = filtered_trades[start_index:end_index]

    return paged_trades


# Endpoint to retrieve a single Trade by ID
@app.get("/trades/{trade_id}", response_model=Trade)
def get_trade_by_id(trade_id: str):
    return mock_db.get(trade_id)


# Generate some random trade data for testing
for _ in range(50):
    trade = generate_random_trade()
    mock_db[trade.trade_id] = trade
