from typing import override

from taker.StrategyTaker import StrategyTaker

class BestTopDownStrategyTaker(StrategyTaker):
    """
    最佳顶底策略
    """
    def __init__(self, g_config,  platform_config, common_config, monitor_interval=4, logger=None, exchangeKey='okx') -> None:
        super().__init__(g_config=g_config,  platform_config=platform_config, common_config=common_config, monitor_interval=monitor_interval, logger=logger, exchangeKey=exchangeKey)
        self.has_init_SL_TPs = {}
        
    @override
    def rest_SL_TP(self, symbol):
        super().rest_SL_TP(symbol)
        if not symbol :
            self.has_init_SL_TPs.clear()
                  
        elif symbol in self.has_init_SL_TPs:
            del self.has_init_SL_TPs[symbol]

    def init_SL_TP(self, symbol: str, position, tfs: dict, strategy: dict) -> bool:
        """
        设置首次止盈止损
        """
        
        precision = self.get_precision_length(symbol)
        # htf = tfs[self.HTF_KEY]
        # etf = tfs[self.ETF_KEY]
        atf = tfs[self.ATF_KEY]
        
        # 1.1  ATF Key Support & Resistance Levels 支撑或阻力关键位置(ATF 看上下的供需区位置）
        atf_df = self.get_historical_klines_df_by_cache(symbol=symbol, tf=atf)
        atf_struct =self.build_struct(symbol=symbol, data=atf_df)
        atf_OBs_df = self.find_OBs(symbol=symbol,struct=atf_struct)
    
        atf_support_OB = self.get_lastest_OB(symbol=symbol,data=atf_OBs_df,trend=self.BULLISH_TREND)
        if atf_support_OB :
            atf_support_price = atf_support_OB.get(self.OB_MID_COL)
        else:
            atf_support_price = atf_struct.at[atf_struct.index[-1], self.STRUCT_LOW_COL]
    
        atf_resistance_OB = self.get_lastest_OB(symbol=symbol,data=atf_OBs_df,trend=self.BEARISH_TREND)
        if atf_resistance_OB :
            atf_resistance_price = atf_resistance_OB.get(self.OB_MID_COL)
        else:
            atf_resistance_price = atf_struct.at[atf_struct.index[-1], self.STRUCT_HIGH_COL]
        self.logger.info(f"{symbol} : ATF {atf}, Key Support={atf_support_price:.{precision}f} "
                         f"& Key Resistance={atf_resistance_price:.{precision}f} ")
        
        side = self.SELL_SIDE if position[self.SIDE_KEY] == self.SHORT_KEY else self.BUY_SIDE # 和持仓反向相反下单
        tick_size = self.get_tick_size(symbol)
        offset = strategy.get('offset',1) # 价格偏移量， 1 代表 1 tick ， 0.000001 代表 1 p
        price_offset = offset * tick_size
        
        if side == self.BUY_SIDE:
            sl_price = self.toDecimal(atf_support_price) - self.toDecimal(price_offset)
            tp_price = self.toDecimal(atf_resistance_price) + self.toDecimal(price_offset)
        else:
            sl_price = self.toDecimal(atf_resistance_price) + self.toDecimal(price_offset)
            tp_price = self.toDecimal(atf_support_price) - self.toDecimal(price_offset)

        self.cancel_all_algo_orders(symbol=symbol, attachType='SL')
        self.set_stop_loss(symbol=symbol, position=position, sl_price=sl_price)
        self.cancel_all_algo_orders(symbol=symbol, attachType='TP')
        self.set_take_profit(symbol=symbol, position=position, tp_price=tp_price)
    
        
        return True

    @override
    def process_pair(self, symbol: str, position, pair_config: dict) -> None:
        """
        处理单个交易对
        """
        
        precision = self.get_precision_length(symbol)
        
        top_down_strategy = pair_config.get('top_down_strategy',{})

        """
        获取策略配置
        """
              
        tfs = {
            self.HTF_KEY: str(top_down_strategy.get(self.HTF_KEY,'4h')) ,
            self.ATF_KEY: str(top_down_strategy.get(self.ATF_KEY,'15m')),
            self.ETF_KEY: str(top_down_strategy.get(self.ETF_KEY, '1m')),
        }
        
        htf = tfs[self.HTF_KEY]
        atf = tfs[self.ATF_KEY]
        etf = tfs[self.ETF_KEY]
        
        self.logger.info(f"{symbol} : TopDownSMC策略 {htf}|{atf}|{etf} \n")
        
        # 1.1 初始化止盈止损
        if symbol not in self.has_init_SL_TPs:      
            has_pass = self.init_SL_TP(symbol, position, tfs, top_down_strategy)
            if has_pass:
                self.has_init_SL_TPs[symbol] = True
        
        
        pass    