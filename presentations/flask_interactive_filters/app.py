
from flask import Flask
from flask import render_template
from flask import request
import pandas as pd

app = Flask(__name__)
 
# selecting department flat data
deps_full_flat = pd.read_csv('../../data-gathering/partial_data/vis_dep_flat.csv')

keys_full_flat = pd.read_csv('../../data-gathering/partial_data/vis_keywords_flat.csv')
keys_full_flat = keys_full_flat.loc[keys_full_flat['visitorId'].isin(list(set(deps_full_flat['visitorId'].values)))]


def FilterVis(deps_flat, keys_flat, dep_target):
    # selecting visitors in target department
    if dep_target is None:
        new_deps_flat = deps_flat
        new_keys_flat = keys_flat
    else:
        target_vis = deps_flat.loc[deps_flat['department'] == dep_target, 'visitorId'].values
        # getting all data from target visitors
        new_deps_flat = deps_flat.loc[deps_flat['visitorId'].isin(target_vis)]
        new_keys_flat = keys_flat.loc[keys_flat['visitorId'].isin(target_vis)]
        # removing target department
        new_deps_flat = new_deps_flat.loc[new_deps_flat['department'] != dep_target]
    # recounting visitors by department inside target dep
    deps_counts = new_deps_flat.groupby('department', as_index=False).agg({'visitorId': lambda x: list(set(x))})
    deps_counts['vis_qtd'] = deps_counts['visitorId'].apply(lambda x: len(x))
    keys_counts = new_keys_flat.groupby('keywords', as_index=False).agg({'visitorId': lambda x: list(set(x))})
    keys_counts['vis_qtd'] = keys_counts['visitorId'].apply(lambda x: len(x))
    # removing unwanted columns and sorting
    deps_counts = deps_counts[['department', 'vis_qtd']].sort_values(by='vis_qtd', ascending=False)
    keys_counts = keys_counts[['keywords', 'vis_qtd']].sort_values(by='vis_qtd', ascending=False)
    return new_deps_flat, new_keys_flat, deps_counts, keys_counts



ini_deps_flat, ini_keys_flat, ini_deps_count, ini_keys_count = FilterVis(deps_full_flat, keys_full_flat, None)

next_deps_flat = ini_deps_flat.copy()
next_deps_count = ini_deps_count.copy()
next_keys_flat = ini_keys_flat.copy()
next_keys_count = ini_keys_count.copy()

filtros = []

tam_lista = 20

deps_lab = next_deps_count['department'].values[:tam_lista]
deps_val = next_deps_count['vis_qtd'].values[:tam_lista]
keys_lab = next_keys_count['keywords'].values[:tam_lista]
keys_val = next_keys_count['vis_qtd'].values[:tam_lista]

@app.route("/chart")
def chart():
    return render_template('chart.html',
                            deps_values=deps_val,
                            deps_labels=deps_lab,
                            filters=filtros,
                            keys_values=keys_val,
                            keys_labels=keys_lab)

@app.route('/_filter_target')
def filter_dept():
    global next_deps_flat
    global next_keys_flat
    global deps_lab
    global deps_val
    global keys_lab
    global keys_val
    global filtros
    dept = request.args.get('dept', '', type=str)
    filtros.append(dept)
    next_deps_flat, next_keys_flat, next_deps_count, next_keys_count = FilterVis(next_deps_flat, next_keys_flat, dept)
    deps_lab = next_deps_count['department'].values[:tam_lista]
    deps_val = next_deps_count['vis_qtd'].values[:tam_lista]
    keys_lab = next_keys_count['keywords'].values[:tam_lista]
    keys_val = next_keys_count['vis_qtd'].values[:tam_lista]
    return render_template('chart.html',
                        deps_values=deps_val,
                        deps_labels=deps_lab,
                        filters=filtros,
                        keys_values=keys_val,
                        keys_labels=keys_lab)

@app.route('/_reset_data')
def reset_data():
    global next_deps_flat
    global next_keys_flat
    global deps_lab
    global deps_val
    global keys_lab
    global keys_val
    global filtros
    filtros = []
    next_deps_flat = ini_deps_flat.copy()
    next_deps_count = ini_deps_count.copy()
    next_keys_flat = ini_keys_flat.copy()
    next_keys_count = ini_keys_count.copy()
    deps_lab = next_deps_count['department'].values[:tam_lista]
    deps_val = next_deps_count['vis_qtd'].values[:tam_lista]
    keys_lab = next_keys_count['keywords'].values[:tam_lista]
    keys_val = next_keys_count['vis_qtd'].values[:tam_lista]
    return render_template('chart.html',
                        deps_values=deps_val,
                        deps_labels=deps_lab,
                        filters=filtros,
                        keys_values=keys_val,
                        keys_labels=keys_lab)

app.run(host='0.0.0.0', 
    port=5001,
    debug=True)

