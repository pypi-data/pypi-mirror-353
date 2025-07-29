# -*- coding: utf-8 -*-
import traceback
from typing import override

from maker.StrategyMaker import StrategyMaker

class BestTopDownStrategyMaker(StrategyMaker):
    def __init__(self, config, platform_config, common_config, logger=None, exchangeKey='okx'):
        super().__init__(config, platform_config, common_config, logger, exchangeKey)
        self.htf_last_struct = {} # 缓存HTF的最后一个结构
        self.logger = logger
        
    @override
    def reset_all_cache(self, symbol):
        """
        重置所有缓存
        """
        super().reset_all_cache(symbol)    
        self.htf_last_struct.pop(symbol, None) 
        self.clear_cache_historical_klines_df(symbol)
        
    @override
    def process_pair(self,symbol,pair_config):
        self.logger.info("-" * 60)
        """_summary_
        HTF (Daily & 4H)
            1.1. Price's Current Trend 市场趋势
            1.2. Who's In Control 供需控制
            1.3. Key Support & Resistance Levels 关键位置
        ATF (1H & 30 Min & 15 Min)
            2.1. Market Condition
            2.2. PD Arrays
            2.3. Liquidity Areas
        ETF (5 Min & 1 Min)
            1. Reversal Signs
            2. PD Arrays
            3. Place Order 

        """
        try:
            # 检查是否有持仓，有持仓不进行下单
            if self.check_position(symbol=symbol) :
                self.reset_all_cache(symbol)
                self.logger.info(f"{symbol} : 有持仓合约，不进行下单。")          
                return           
            precision = self.get_precision_length(symbol)
            
            top_down_strategy = pair_config.get('top_down_strategy',{})

            """
            获取策略配置
            """
            htf = str(top_down_strategy.get('HTF','4h'))  
            atf = str(top_down_strategy.get('ATF','15m'))
            etf = str(top_down_strategy.get('ETF', '1m')) 

            self.logger.info(f"{symbol} : TopDownSMC策略 {htf}|{atf}|{etf} \n")
            market_price = self.get_market_price(symbol=symbol)
            
            """
            step 1 : Higher Time Frame Analysis
            """
            step = "1"
            # 初始化HTF趋势相关变量
            htf_side, htf_struct, htf_trend = None, None, None
            # HTF 缓存，减小流量损耗            
            htf_df = self.get_historical_klines_df_by_cache(symbol=symbol, tf=htf)
            htf_struct =self.build_struct(symbol=symbol, data=htf_df)
            
            htf_latest_struct = self.get_last_struct(symbol=symbol, data=htf_struct)

            htf_trend = self.BULLISH_TREND if htf_latest_struct[self.STRUCT_DIRECTION_COL] == 1 else self.BEARISH_TREND
            htf_side = self.BUY_SIDE if htf_trend == self.BULLISH_TREND else self.SELL_SIDE
            # 1.1. Price's Current Trend 市场趋势（HTF）
            step = "1.1"
            self.logger.info(f"{symbol} : {step}. HTF {htf} Price's Current Trend is {htf_trend}。")
            # 1.2. Who's In Control 供需控制，Bullish 或者 Bearish ｜ Choch 或者 BOS
            step = "1.2"
            self.logger.info(f"{symbol} : {step}. HTF {htf} struct is {htf_latest_struct[self.STRUCT_COL]}。")

            # 1.3. HTF Key Support & Resistance Levels 支撑或阻力关键位置(HTF 看上下的供需区位置）
            step = "1.3"
            htf_OBs_df = self.find_OBs(symbol=symbol,struct=htf_struct)

            if htf_OBs_df is None or len(htf_OBs_df) == 0:
                self.logger.debug(f"{symbol} : {step}. HTF {htf} 未找到OB。")
                return
            else:
                self.logger.debug(f"{symbol} : {step}. HTF {htf} 找到OB。")
            
                htf_support_OB = self.get_lastest_OB(symbol=symbol,data=htf_OBs_df,trend=self.BULLISH_TREND)
                if htf_support_OB :
                    htf_support_price = htf_support_OB.get(self.OB_MID_COL)
                else:
                    htf_support_price = htf_struct.at[htf_struct.index[-1], self.STRUCT_LOW_COL]
            
                htf_resistance_OB = self.get_lastest_OB(symbol=symbol,data=htf_OBs_df,trend=self.BEARISH_TREND)
                if htf_resistance_OB :
                    htf_resistance_price = htf_resistance_OB.get(self.OB_MID_COL)
                else:
                    htf_resistance_price = htf_struct.at[htf_struct.index[-1], self.STRUCT_HIGH_COL]
                self.logger.info(f"{symbol} : {step}. HTF {htf}, Key Support={htf_support_price:.{precision}f} & Key Resistance={htf_resistance_price:.{precision}f} ")
            #1.4. 检查关键支撑位和阻力位之间是否有利润空间。
            step = "1.4"
            # 计算支撑位和阻力位之间的利润空间百分比
            htf_profit_percent = abs((htf_resistance_price - htf_support_price) / htf_support_price * 100)
            min_profit_percent = pair_config.get('min_profit_percent', 4) # 默认最小利润空间为0.5%

            if htf_profit_percent < min_profit_percent:
                self.logger.info(f"{symbol} : {step}. HTF {htf} 支撑位={htf_support_price:.{precision}f} 与阻力位={htf_resistance_price:.{precision}f} 之间利润空间{htf_profit_percent:.2f}% < {min_profit_percent}%，等待...")
                return
            else:
                self.logger.info(f"{symbol} : {step}. HTF {htf} 支撑位={htf_support_price:.{precision}f} 与阻力位={htf_resistance_price:.{precision}f} 之间利润空间{htf_profit_percent:.2f}% >= {min_profit_percent}%")
                            
            # 1.5. 检查当前价格是否在关键支撑位和阻力位，支撑位可以做多，阻力位可以做空。
            step = "1.5"
            htf_ce_price = (htf_support_price + htf_resistance_price) / 2
            # 折价区
            target_trend = self.BULLISH_TREND if (market_price >= htf_support_price and market_price < htf_ce_price)  else self.BEARISH_TREND
            # FIXME target_trend 更新 htf_trend
            htf_trend = target_trend
            if target_trend != htf_trend:
                self.logger.info(f"{symbol} : {step}. HTF {htf} 目标趋势 {target_trend} 与当前趋势 {htf_trend} 不符，折价区 ce={htf_ce_price:.{precision}f} ，等待...")
                return
            else:
                self.logger.info(f"{symbol} : {step}. HTF {htf} 目标趋势 {target_trend} 与当前趋势 {htf_trend} 一致， ce={htf_ce_price:.{precision}f}")
                
            """
            step 2 : Analysis Time Frames
            """
            # 2. ATF Step 
            # 2.1 Market Condition 市场状况（ATF 看上下的供需区位置）
            
            atf_side, atf_struct, atf_trend = None, None, None
            atf_df = self.get_historical_klines_df(symbol=symbol, tf=atf)
            atf_struct =self.build_struct(symbol=symbol, data=atf_df)            
            atf_latest_struct = self.get_last_struct(symbol=symbol, data=atf_struct)
            atf_trend = atf_latest_struct[self.STRUCT_DIRECTION_COL]
            atf_side = self.BUY_SIDE if atf_trend == self.BULLISH_TREND else self.SELL_SIDE
            # 2.1. Price's Current Trend 市场趋势（HTF ）
            step = "2.1"
            self.logger.info(f"{symbol} : {step}. ATF {atf} Price's Current Trend is {atf_trend}。")
            # 2.2. Who's In Control 供需控制，Bullish 或者 Bearish ｜ Choch 或者 BOS
            step = "2.2"
            self.logger.info(f"{symbol} : {step}. ATF {atf} struct is {atf_latest_struct[self.STRUCT_COL]}。")
            # TODO 2.3. 检查关键支撑位和阻力位之间是否有利润空间。
            
            # 2.4. ATF 方向要和 HTF方向一致
            step = "2.4"
     
            if htf_trend != atf_trend:
                self.logger.info(f"{symbol} : {step}. ATF {atf} is {atf_trend} 与 HTF {htf} is {htf_trend} 不一致，等待...")
                return
            else:
                self.logger.info(f"{symbol} : {step}. ATF {atf} is {atf_trend} 与 HTF {htf} is {htf_trend} 一致。")
            #TODO 2.5. check Liquidity Areas ，检查当前结构是否是流动性摄取。
            
            

            # 2.6. 在HTF供需区范围，找ATF的PDArray，FVG和OB，供需区，计算监测下单区域范围。
            setp = "2.6"
            atf_pdArrays_df = self.find_PDArrays(symbol=symbol,struct=atf_struct,side=atf_side)
            
            # 不同的结构，不同位置，如果是Choch则等待价格进入PDArray，如果是BOS则等待价格进入折价区
            # 划分 折价(discount)区和溢价(premium)区
            atf_struct_high = atf_latest_struct[self.STRUCT_HIGH_COL]
            atf_struct_low = atf_latest_struct[self.STRUCT_LOW_COL]            
            atf_struct_mid = atf_latest_struct[self.STRUCT_MID_COL]
            
            if "CHOCH" in atf_struct[self.STRUCT_COL]:
                # 找PDArray,Bullish 则PDArray的mid要小于 atf_struct_mid，Bearish 则PDArray的mid要大于 atf_struct_mid
                # atf_discount_mid = (atf_struct_mid + atf_struct_high) / 2  if atf_trend == self.BEARISH_TREND else (atf_struct_mid + atf_struct_low) / 2
                mask = atf_pdArrays_df[self.PD_MID_COL] >= atf_struct_mid if atf_trend == self.BEARISH_TREND else atf_pdArrays_df[self.PD_MID_COL] <= atf_struct_mid
                atf_pdArrays_df = atf_pdArrays_df[mask]
                if len(atf_pdArrays_df) == 0:
                    self.logger.info(f"{symbol} : {setp}.1. ATF {atf} 未找到PDArray，不下单")
                    return
                else:
                    # 找到最新的PDArray              
                    atf_vaild_pdArray = atf_pdArrays_df.iloc[-1]
                    self.logger.info(f"{symbol} : {setp}.1. ATF {atf} 找到PDArray\n"
                        f"{atf_vaild_pdArray[[self.TIMESTAMP_COL,self.PD_TYPE_COL,self.PD_HIGH_COL,self.PD_LOW_COL,self.PD_MID_COL]]}。")
               
            
            #SMS
            elif "SMS" in atf_struct[self.STRUCT_COL]:
                mask = atf_pdArrays_df[self.PD_MID_COL] >= atf_struct_mid if atf_trend == self.BEARISH_TREND else atf_pdArrays_df[self.PD_MID_COL] <= atf_struct_mid
                atf_pdArrays_df = atf_pdArrays_df[mask]
                if len(atf_pdArrays_df) == 0:
                    self.logger.info(f"{symbol} : {setp}.1. ATF {atf} 在{atf_struct_mid:.{precision}f}未找到PDArray，不下单")
                    return
                else:
                    # 找到最新的PDArray              
                    atf_vaild_pdArray = atf_pdArrays_df.iloc[-1]
                    self.logger.info(f"{symbol} : {setp}.1. ATF {atf} 找到PDArray\n"
                        f"{atf_vaild_pdArray[[self.TIMESTAMP_COL,self.PD_TYPE_COL,self.PD_HIGH_COL,self.PD_LOW_COL,self.PD_MID_COL]]}。")
               

            #BMS   
            else:
                atf_premium_mid = (atf_struct_mid + atf_struct_low) / 2  if atf_trend == self.BEARISH_TREND else (atf_struct_mid + atf_struct_high) / 2
                mask = atf_pdArrays_df[self.PD_HIGH_COL] >= atf_premium_mid if atf_trend == self.BEARISH_TREND else atf_pdArrays_df[self.PD_LOW_COL] <= atf_premium_mid
                atf_pdArrays_df = atf_pdArrays_df[mask]
                if len(atf_pdArrays_df) == 0:
                    self.logger.info(f"{symbol} : {setp}.1. ATF {atf} ,在{atf_premium_mid:.{precision}f}未找到PDArray，不下单")
                    return
                else:
                    # 找到最新的PDArray              
                    atf_vaild_pdArray = atf_pdArrays_df.iloc[-1]
                    self.logger.info(f"{symbol} : {setp}.1. ATF {atf} 找到PDArray\n"
                        f"{atf_vaild_pdArray[[self.TIMESTAMP_COL,self.PD_TYPE_COL,self.PD_HIGH_COL,self.PD_LOW_COL,self.PD_MID_COL]]}")
               
              
            
            setp = "2.7"

            # 2.7. 等待价格进入 PDArray
       
            if not (market_price <= atf_vaild_pdArray[self.PD_HIGH_COL] and market_price >= atf_vaild_pdArray[self.PD_LOW_COL]):
                self.logger.info(f"{symbol} : {setp}. ATF {atf} market_price={market_price:.{precision}f} 未达到PDArray范围。"
                                f"PD_HIGH={atf_vaild_pdArray[self.PD_LOW_COL]:.{precision}f} "
                                f"PD_LOW={atf_vaild_pdArray[self.PD_HIGH_COL]:.{precision}f} ")

                return 
            else:
                self.logger.info(f"{symbol} : {setp}. ATF {atf} market_price={market_price:.{precision}f} 已到达PDArray范围。"
                                f"PD_HIGH={atf_vaild_pdArray[self.PD_LOW_COL]:.{precision}f} "
                                f"PD_LOW={atf_vaild_pdArray[self.PD_HIGH_COL]:.{precision}f} ")


            # 3. ETF Step 

            etf_side, etf_struct, etf_trend = None, None, None
            etf_df = self.get_historical_klines_df(symbol=symbol, tf=etf)                   
            etf_struct =self.build_struct(symbol=symbol, data=etf_df)            
            etf_latest_struct = self.get_last_struct(symbol=symbol, data=etf_struct)

            # 初始化HTF趋势相关变量
            
            etf_trend = etf_latest_struct[self.STRUCT_DIRECTION_COL]
            #FIXME etf_trend
            etf_trend = atf_trend
            
            etf_side = self.BUY_SIDE if etf_trend == self.BULLISH_TREND else self.SELL_SIDE

            # 3.1. Price's Current Trend 市场趋势（ETF ）
            setp = "3.1"
            self.logger.info(f"{symbol} : {setp}. ETF {etf} Price's Current Trend is {etf_trend}。")
            # 3.2. Who's In Control 供需控制，Bullish 或者 Bearish ｜ Choch 或者 BOS
            setp = "3.2"
            self.logger.info(f"{symbol} : {setp}. ETF {etf} struct is {etf_latest_struct[self.STRUCT_COL]}。")
            

            # 3.3 Reversal Signs 反转信号
            setp = "3.3"
    
            if atf_trend != etf_trend:
        
                self.logger.info(f"{symbol} : {setp}. ETF {etf} 市场结构{etf_latest_struct[self.STRUCT_COL]}未反转,等待...")
                return
            else:
                self.logger.info(f"{symbol} : {setp}. ETF {etf} 市场结构{etf_latest_struct[self.STRUCT_COL]}已反转。")

            # TODO "CHOCH"|"BOS" 的PDArray 入场位置不一样

            # 3.4 找 PD Arrays 价格区间（ETF 看上下的供需区位置）
            setp = "3.4"
            etf_pdArrays_df = self.find_PDArrays(symbol=symbol,struct=etf_struct,side=etf_side)
            # 划分 折价(discount)区和溢价(premium)区
            etf_struct_high = etf_latest_struct[self.STRUCT_HIGH_COL]
            etf_struct_low = etf_latest_struct[self.STRUCT_LOW_COL]            
            etf_struct_mid = etf_latest_struct[self.STRUCT_MID_COL]
            mask = etf_pdArrays_df[self.PD_MID_COL] >= etf_struct_mid if etf_trend == self.BEARISH_TREND else etf_pdArrays_df[self.PD_MID_COL] <= etf_struct_mid
            etf_pdArrays_df = etf_pdArrays_df[mask]
            if len(etf_pdArrays_df) == 0:
                self.logger.info(f"{symbol} : {setp}.1. ETF {etf} 未找到PDArray，不下单")
                return
            else:
                # 找到最新的PDArray              
                etf_vaild_pdArray = etf_pdArrays_df.iloc[-1]
                self.logger.info(f"{symbol} : {setp}.1. ETF {etf} 找到PDArray.\n"
                                f"{etf_vaild_pdArray[[self.TIMESTAMP_COL,self.PD_TYPE_COL,self.PD_HIGH_COL,self.PD_LOW_COL,self.PD_MID_COL]]}。")
               
       
            if not (market_price <= etf_vaild_pdArray[self.PD_HIGH_COL] and market_price >= etf_vaild_pdArray[self.PD_LOW_COL]):
                self.logger.info(f"{symbol} : {setp}.2. ETF {etf} market_price={market_price:.{precision}f} 未达到PDArray范围。"
                                  f"PD_HIGH={etf_vaild_pdArray[self.PD_HIGH_COL]:.{precision}f} "
                                  f"PD_LOW={etf_vaild_pdArray[self.PD_LOW_COL]:.{precision}f}")

                return 
            else:
                self.logger.info(f"{symbol} : {setp}.2. ETF {etf} market_price={market_price:.{precision}f} 已到达PDArray范围。"
                                  f"PD_HIGH={etf_vaild_pdArray[self.PD_HIGH_COL]:.{precision}f} "
                                  f"PD_LOW={etf_vaild_pdArray[self.PD_LOW_COL]:.{precision}f}")    

            # 3.5 Place Order 下单
            setp = "3.5"
            # order_price = self.toDecimal(etf_vaild_pdArray[self.PD_HIGH_COL] if etf_trend == self.BULLISH_TREND else etf_vaild_pdArray[self.PD_LOW_COL] )
            order_price = self.toDecimal(etf_vaild_pdArray[self.PD_MID_COL])  
            
            latest_order_price = self.toDecimal(self.place_order_prices.get(symbol,0))
            if order_price == latest_order_price:
                self.logger.info(f"{symbol} : {setp}. ETF {etf}, 下单价格 {order_price:.{precision}} 未变化，不进行下单。")
                return
            
            self.cancel_all_orders(symbol=symbol) 
            self.place_order(symbol=symbol, price=order_price, side=etf_side, pair_config=pair_config)
            self.place_order_prices[symbol] = order_price # 记录下单价格,过滤重复下单
            self.logger.info(f"{symbol} : {setp}. ETF {etf}, {etf_side} 价格={order_price:.{precision}}")


        except KeyboardInterrupt:
            self.logger.info("程序收到中断信号，开始退出...")
        except Exception as e:
            error_message = f"程序异常退出: {str(e)}"
            self.logger.error(error_message,exc_info=True)
            traceback.print_exc()
            self.send_feishu_notification(symbol, error_message)
        finally:
            self.logger.info("=" * 60 + "\n")
  
            

        
