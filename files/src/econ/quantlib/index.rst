Quantlib (★)
================

Reference:

* http://gouthamanbalaraman.com/blog/quantlib-python-tutorials-with-examples.html

Confirm the above reference code below. 



#. Scheduleの使い方

    You need to set marktet. eg. 

    :: 

        calendar = ql.UnitedStates(ql.UnitedStates.NYSE)

    Reviewed code

    .. jupyter-execute::

        import QuantLib as ql
        date1 = ql.Date(1, 1, 2015)

        date2 = date1 + ql.Period(1, ql.Years)
        tenor = ql.Period(ql.Monthly)
        #参考文献ではエラーが発生する。マーケットをパスする必要がある。
        calendar = ql.UnitedStates(ql.UnitedStates.NYSE)
        schedule = ql.Schedule(date1, date2, tenor, calendar, ql.Following, ql.Following, ql.DateGeneration.Forward, False)
        list(schedule)



#. 福利計算

    .. jupyter-execute::

        import QuantLib as ql

        todaysDate = ql.Date(15, 1, 2015)
        #annualRate = 0.05
        ##dayCount = ql.ActualActual()
        #compoundType = ql.Compounded
        #frequency = ql.Annual
        #interestRate = ql.InterestRate(annualRate, dayCount, compoundType, frequency)

        #print(interestRate.compoundFactor(2.0))

        #print((1.0 + annualRate)*(1.0 + annualRate))

#. 債券計算

    - 発行日：2015年 Jan



#. イールドカーブ
    
    - 発行日    


#. ハルホワイトモデル


