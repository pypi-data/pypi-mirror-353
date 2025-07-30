import datetime
import grpc
import pandas as pd
import pyarrow as pa

from .input import (
    DateTimeArgType,
    StrListArgType,
    ParamArgType,
    parse_datetime_arg,
    parse_str_list_arg,
    parse_param_arg
)
from .pb import service_pb2, service_pb2_grpc
from .time_util import LOCAL_TIME_OFFSET


__all__ = [
    'DataClient'
]


class _TableService:
    def __init__(self, channel: grpc.Channel, name: str):
        self._name = name
        self._stub = service_pb2_grpc.PDataServiceStub(channel)

    def intersect(
        self,
        fields: StrListArgType = None,
        since: DateTimeArgType = None,
        until: DateTimeArgType = None,
        params: ParamArgType = None
    ):
        return self._perform_query(
            query_type=service_pb2.QueryType.QUERY_TYPE_INTERVAL,
            index_count=1,
            fields=fields,
            since=since,
            until=until,
            params=params
        )

    def range(
        self,
        ids: StrListArgType = None,
        fields: StrListArgType = None,
        since: DateTimeArgType = None,
        until: DateTimeArgType = None,
        use_local_time: bool = False,
        params: ParamArgType = None
    ):
        return self._perform_query(
            query_type=service_pb2.QueryType.QUERY_TYPE_TIME,
            index_count=1,
            ids=ids,
            fields=fields,
            since=since,
            until=until,
            use_local_time=use_local_time,
            params=params
        )

    def _perform_query(
        self,
        query_type: service_pb2.QueryType,
        index_count: int,
        ids: StrListArgType = None,
        fields: StrListArgType = None,
        since: DateTimeArgType = None,
        until: DateTimeArgType = None,
        use_local_time: bool = False,
        params: ParamArgType = None
    ):
        params = parse_param_arg(params)
        param_list = []
        for k, v in params.items():
            param_list.append(service_pb2.RequestParam(
                name=k,
                values=v
            ))
        request = service_pb2.GetTableDataRequest(
            name=self._name,
            query_type=query_type,
            ids=parse_str_list_arg(ids),
            fields=parse_str_list_arg(fields),
            since=parse_datetime_arg(since, use_local=use_local_time),
            until=parse_datetime_arg(until, use_local=use_local_time, default_now=True),
            params=param_list
        )

        cursor = self._stub.GetTableData(request=request)

        batches = []
        is_date_series = False
        for chunk in cursor:
            is_date_series = chunk.is_date_series
            with pa.ipc.open_stream(chunk.data) as reader:
                try:
                    while True:
                        batch = reader.read_next_batch()
                        batches.append(batch)
                except StopIteration:
                    pass
        table = pa.Table.from_batches(batches)
        df: pd.DataFrame = table.to_pandas()

        if not is_date_series and use_local_time:
            for i in range(index_count):
                if df.iloc[:, i].dtype == 'datetime64[ms]':
                    df.iloc[:, i] = df.iloc[:, i] + datetime.timedelta(milliseconds=LOCAL_TIME_OFFSET)

        return df.set_index(list(df.columns)[:index_count])


class _TradingDayService:
    def __init__(self, channel: grpc.Channel):
        self._service = _TableService(channel, 'CALENDAR')

    def is_trading_day(
            self,
            dt: DateTimeArgType = None,
            calendar: str = 'CN'
    ) -> bool:
        df = self._service.range(
            ids=[calendar],
            since=dt,
            until=dt
        )
        nr, _ = df.shape
        return nr > 0

    def range(
        self,
        start_dt: DateTimeArgType = None,
        end_dt: DateTimeArgType = None,
        calendar: str = 'CN'
    ):
        df = self._service.range(
            ids=[calendar],
            since=start_dt,
            until=end_dt
        )
        return [x.to_pydatetime() for x in df.index]


class DataClient:
    def __init__(self, host: str, port: int):
        self._channel = grpc.insecure_channel(f'{host}:{port}')

    def table(self, name: str):
        return _TableService(self._channel, name)

    @property
    def trading_day(self):
        return _TradingDayService(self._channel)
