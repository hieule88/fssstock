import pandas as pd
import numpy as np
import os
import csv

#Process the data for the chart - main
def main_series(df, v_dimension):
    try:
        arrfield=['THUETNDN','LOINHUAN']
        newdf=pd.pivot_table(df, index=[v_dimension],values=arrfield,aggfunc=np.sum)
        categories=list(newdf.index)
        row = []
        for fld in arrfield:
            data=[]
            for item_name, rec in newdf.iterrows():
                data.append(rec[fld])
            row.append(
                {
                    'name': fld,
                    'data': data
                }
            )      
        return categories, row
    except:
        # Re-raise the exception.
        raise        


#Process the data for the chart - pie with drilldown
def pie_series(df, v_measure, v_dimension, v_subcode):
    try:
        rs = df.groupby(v_dimension)[v_measure].agg("sum")
        categories = list(rs.index)
        values = list(rs.values)
        size_of_series = len(categories)
        row = []
        subrow = []
        for i in range(size_of_series):
            rowcolname=str(categories[i])
            if rowcolname=='OTH':
                row.append(
                    {
                        'name': rowcolname,
                        'y': values[i],
                        'drilldown': ''
                    }
                )
            else:
                row.append(
                    {
                        'name': rowcolname,
                        'y': values[i],
                        'drilldown':  rowcolname
                    }
                )
            newdf = df.loc[df[v_dimension] == categories[i]]
            subrs = newdf.groupby([v_subcode])[v_measure].agg("sum")
            subcategories = list(subrs.index)
            subvalues = list(subrs.values)	
            subsize_of_series = len(subcategories)
            data = []
            for k in range(subsize_of_series):
                item = [str(subcategories[k]),subvalues[k]]
                data.append(item)
            subrow.append(
                {
                    'name': rowcolname,
                    'id': rowcolname,
                    'data': data
                }
            )
        return row, subrow
    except:
        # Re-raise the exception.
        raise        

#Process the data for the chart - scatter
def scatter_series(df, v_measure, v_dimension):
    try:
        rs = df.groupby(v_dimension)[v_measure].agg("sum")
        categories = list(rs.index)
        size_of_series = len(categories)
        row = []
        for i in range(size_of_series):
            v_serie_name = categories[i]
            newdf = df.loc[(df[v_dimension] == v_serie_name)]
            data = []
            for index, rec in newdf.iterrows():
                item = [rec["THUETNDN_GL"], rec["TL_GL"]]
                data.append(item)
            row.append(
                {
                    'name': v_serie_name,
                    'data': data
                }
            )        
        return row
    except:
        # Re-raise the exception.
        raise        

#Process the data for the chart - heatmap
def heatmap_series(df, v_measure, v_dimension, v_subcode):
    try:
        rs = df.groupby(v_subcode)[v_measure].agg("sum")
        categories = list(rs.index)
        size_of_yseries = len(categories)
        y_categories = []
        for i in range(size_of_yseries):
            y_categories.append(categories[i])

        rs = df.groupby(v_dimension)[v_measure].agg("sum")
        categories = list(rs.index)
        size_of_xseries = len(categories)
        x_categories = []
        for i in range(size_of_xseries):
            x_categories.append(categories[i])

        data = []
        for i in range(size_of_yseries):
            for k in range(size_of_xseries):
                newdf = df.loc[(df[v_dimension] == x_categories[k]) & (df[v_subcode] == y_categories[i])]
                totalval = round(newdf[v_measure].sum(),2)
                item = [k,i,totalval]
                data.append(item)
        return x_categories, y_categories, data
    except:
        # Re-raise the exception.
        raise        

#Process the data for the chart - sunburst
def sunburst_series(df, v_measure, v_dimension, v_subcode):
    try:
        rs = df.groupby(v_dimension)[v_measure].agg("sum")
        categories = list(rs.index)

        size_of_series = len(categories)
        row = []
        nodeid_id = '0.0'
        row.append(
            {
                'id': nodeid_id,
                'parent': '',
                'name': 'ALL'
            }
        )
        parent_id = '0.0'
        for i in range(size_of_series):
            nodeid_id = '1.' + str(i+1)
            row.append(
                {
                    'id': nodeid_id,
                    'parent': parent_id,
                    'name': categories[i]
                }
            )
        for i in range(size_of_series):
            parent_id = '1.' + str(i+1)
            newdf = df.loc[df[v_dimension] == categories[i]]
            subrs = newdf.groupby([v_subcode])[v_measure].agg("sum")
            subcategories = list(subrs.index)
            subvalues = list(subrs.values)
            subsize_of_series = len(subcategories)
            for k in range(subsize_of_series):
                nodeid_id = '2.' + str(k+1)
                row.append(
                    {
                        'id': nodeid_id,
                        'parent': parent_id,
                        'name': subcategories[k],
                        'value': subvalues[k],
                    }
                )    
        return row
    except:
        # Re-raise the exception.
        raise        
    
#Process the data for the chart - bubble
def bubble_series(df, v_measure, v_dimension, v_subcode):
    try:
        rs = df.groupby(v_dimension)[v_measure].agg("sum")
        categories = list(rs.index)

        size_of_series = len(categories)
        row = []
        for i in range(size_of_series):
            newdf = df.loc[df[v_dimension] == categories[i]]
            subrs = newdf.groupby([v_subcode])[v_measure].agg("sum")
            subcategories = list(subrs.index)
            subvalues = list(subrs.values)
            subsize_of_series = len(subcategories)
            data = []
            for k in range(subsize_of_series):
                item = [str(subcategories[k]),subvalues[k]]
                data.append(item)
            row.append(
                {
                    'name': categories[i],
                    'data': data
                }
            )
        return row
    except:
        # Re-raise the exception.
        raise        

#Process the data for the chart - drilldown
def drilldown_series(df, v_measure, v_dimension, v_subcode):
    try:
        rs = df.groupby(v_dimension)[v_measure].agg("sum")
        categories = list(rs.index)
        values = list(rs.values)
        size_of_series = len(categories)
        row = []
        subrow = []
        for i in range(size_of_series):
            rowcolname=str(categories[i])
            if rowcolname=='OTH':
                row.append(
                    {
                        'name': rowcolname,
                        'y': values[i],
                        'drilldown': ''
                    }
                )
            else:
                row.append(
                    {
                        'name': rowcolname,
                        'y': values[i],
                        'drilldown':  rowcolname
                    }
                )
            newdf = df.loc[df[v_dimension] == categories[i]]
            subrs = newdf.groupby([v_subcode])[v_measure].agg("sum")
            subcategories = list(subrs.index)
            subvalues = list(subrs.values)	
            subsize_of_series = len(subcategories)
            data = []
            for k in range(subsize_of_series):
                item = [str(subcategories[k]),subvalues[k]]
                data.append(item)
            subrow.append(
                {
                    'name': rowcolname,
                    'id': rowcolname,
                    'data': data
                }
            )
        return row, subrow
    except:
        # Re-raise the exception.
        raise        

#Process the data for the chart - drilldown
def comparison_series(df, v_measure, v_dimension, v_subcode):
    try:
        rs = df.groupby(v_subcode)[v_measure].agg("sum")
        categories = list(rs.index)
        size_of_series = len(categories)
        comparison_year=[]
        thisdict = {}
        for i in range(size_of_series):
            v_year=categories[i]
            newdf = df.loc[df[v_subcode] == v_year]
            subrs = newdf.groupby([v_dimension])[v_measure].agg("sum")
            subcategories = list(subrs.index)
            subvalues = list(subrs.values)
            subsize_of_series = len(subcategories)
            data = []
            for k in range(subsize_of_series):
                item = [str(subcategories[k]),subvalues[k]]
                data.append(item)
            comparison_year.append(v_year)
            thisdict[v_year] = data
        comparison_series = thisdict

        v_start_year = min(comparison_year)
        thisdict = {}
        for v_year in comparison_year:
            if v_year>v_start_year:
                thisdict[v_year] = comparison_series[v_year-1]
            else:
                thisdict[v_year] = comparison_series[v_year]
        comparison_prev_series = thisdict
        return comparison_year, comparison_prev_series, comparison_series
    except:
        # Re-raise the exception.
        raise        
