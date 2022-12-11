import streamlit as st
import pandas as pd
import altair as alt
from altair import datum


st.set_page_config(
    page_title="Florida Inmates and Their Tattoos",
    page_icon="🎨",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# This app will provide insite on Florida prisoners' tattoos and charges."
    }
)


@st.experimental_memo
def load_data():
    offenses = pd.read_parquet('./data/offense_inmate.parquet')
    ts_charges = pd.read_parquet('./data/ts_charges.parquet')
    off_groups = offenses.groupby('County').agg({'prisonterm': 'mean',
                                                'ProbationTerm': 'mean',
                                                 'ParoleTerm': 'mean',
                                                 'DCNumber': 'count'
                                                 })
    off_groups.reset_index(inplace=True)
    counties = list(offenses.County.unique())
    counties.append('ALL')
    counties.sort()
    return offenses, ts_charges, ts_charges.charge.unique(), off_groups, counties


offenses, ts_charges, charges, off_groups, counties = load_data()


def refresh_charts(offenses=offenses, ts_charges=ts_charges, charges=charges, off_groups=off_groups):
    county = 'ALL'
    if 'charges' in st.session_state:
        charges = st.session_state['charges']
    else:
        st.session_state['charges'] = ['1ST DG MUR/PREMED. OR ATT.',
                                       '2ND DEG.MURD,DANGEROUS ACT',
                                       'ESCAPE',]
        charges = st.session_state['charges']

    if 'county' in st.session_state:
        county = st.session_state['county']
        if county != 'ALL':
            offenses = offenses.loc[offenses['County'] == county]

    race = offenses.groupby(['County', 'Race', 'Sex']).agg({
        'DCNumber': 'count'
    }).reset_index()

    date_mask = (ts_charges['year'] > '1970-01-01') & (ts_charges['year']
                                                       <= '2016-01-01') & (ts_charges['charge'].isin(charges))

    ts_line = alt.Chart(ts_charges.loc[date_mask]).mark_line().encode(
        alt.X('year:T', title='Year of Offense'),
        alt.Y('sum(DCNumber):Q', title='Count'),
        color=alt.Color('charge:N', title='Charge',
                        scale=alt.Scale(scheme='category20c')),
        tooltip=[
            alt.Tooltip("charge", title="Charge"),
            alt.Tooltip("year", title="Year"),
            alt.Tooltip("sum(DCNumber)", title="Count of Charge"),
        ]
    ).properties(width=900, height=450, title=f"Charges by Year of Offense",
                 )
    release_bump = offenses.groupby([offenses.OffenseDate.dt.year, 'releasedateflag_descr']).agg({
        'DCNumber': 'count'}).reset_index()

    bump = alt.Chart(release_bump.loc[release_bump['OffenseDate'] > 1984]).mark_line(point=True).encode(
        x=alt.X("OffenseDate:O", title="date"),
        y="rank:O",
        color=alt.Color("releasedateflag_descr:N",
                        scale=alt.Scale(scheme='category20c'), title='Release Date Flag'),
        tooltip=[
            alt.Tooltip("OffenseDate", title="Year of Offense"),
            alt.Tooltip("releasedateflag_descr",
                        title="Release Date Flag"),
            alt.Tooltip("DCNumber", title="Count"),


        ]
    ).transform_window(
        rank="rank()",
        sort=[alt.SortField("DCNumber", order="descending")],
        groupby=["OffenseDate"]
    ).properties(
        title=f"Bump Chart for Release Flag for {county}",
    )

    return off_groups, race, ts_line, bump


off_groups, race, ts_line, bump = refresh_charts()

# @st.cache(allow_output_mutation=True)


def col_charts(max_results=15):
    tot_bar = alt.Chart(race).transform_aggregate(
        sum='sum(DCNumber)',
        groupby=['County']
    ).transform_window(
        rank='rank(sum)',
        sort=[alt.SortField('sum', order='descending')]
    ).transform_filter(
        datum.rank <= max_results
    ).mark_bar().encode(
        alt.Y('County:N', sort='-x'),
        alt.X('sum:Q', title='Number of Offenses'),
        color=alt.Color('Race')
    )
    race_bar = alt.Chart(off_groups).mark_bar().encode(
        alt.X('DCNumber:Q', axis=alt.Axis(title='Count')),
        alt.Y('County:N', sort='-x'),
        color=alt.Color('prisonterm', title='Mean Prison Term',
                        scale=alt.Scale(scheme='yelloworangered'))
    ).transform_window(
        rank='rank(DCNumber)',
        sort=[alt.SortField('DCNumber', order='descending')]
    ).transform_filter(
        datum.rank < max_results
    ).properties(width=500, height=400, title='Count of Offenses by County')
    county_race = race.groupby(['County', 'Race']).agg({
        'DCNumber': 'sum'
    }).reset_index()
    race_off_bar = alt.Chart(county_race).mark_bar().encode(
        alt.X('ranked_race:N', title='Race', sort=alt.Sort(
            op="sum", field="sum_offenses", order="descending")),
        alt.Y('sum_offenses:Q', title='Sum of Offenses'),
        color=alt.Color('Race:N', scale=alt.Scale(
            scheme='yelloworangered'))
    ).transform_aggregate(
        sum_offenses='sum(DCNumber)',
        groupby=["Race"],
    ).transform_window(
        rank='row_number()',
        sort=[alt.SortField("sum_offenses", order="descending")],
    ).transform_calculate(
        ranked_race="datum.rank < 3 ? datum.Race : 'All Others'"
    ).properties(width=200, height=400, title='Count of Offenses by Race')

    xList = ['valid release date', 'life sentence',
             'coterminous Florida and other state/federal custody', 'death sentence',
             'pending', 'to be set']
    yList = ['W', 'B', 'H', 'U', 'I', 'A']
    xDict = pd.DataFrame(
        {'id': xList, 'rd_code': list(range(0, len(xList)))})
    yDict = pd.DataFrame(
        {'id': yList, 'race_code': list(range(0, len(yList)))})

    df_off = pd.merge(offenses, xDict, how='left',
                      left_on='releasedateflag_descr', right_on='id')
    df_off = pd.merge(df_off, yDict, how='left',
                      left_on='Race', right_on='id')

    dr_gpb = df_off[['Race',
                    'prisonterm',
                     'releasedateflag_descr',
                     'race_code',
                     'County',
                     'rd_code']].groupby(['releasedateflag_descr', 'Race'], as_index=False).agg({'prisonterm': ['mean', 'max'], 'race_code': 'max', 'rd_code': 'max'})
    dr_gpb = pd.DataFrame(dr_gpb.to_records())
    # print(dr_gpb.columns)
    flatt_cols = [remove_special_characters(c) for c in dr_gpb.columns]
    dr_gpb.columns = flatt_cols
    gbp = alt.Chart(dr_gpb).mark_bar().encode(
        alt.X("Race:N", title='Race'),
        alt.Y("mean(prisontermmean):Q",
              title='Mean Prison Term by Days'),
        color=alt.Color("Race:N", scale=alt.Scale(
            scheme='yelloworangered')),
    ).properties(width=400, height=400, title='Mean Prison term by Race')

    return tot_bar, race_bar, race_off_bar, gbp


def remove_special_characters(s):
    return ''.join(e for e in s if e.isalnum())


st.header('Florida Prisoner Offenses')

ovv_tab, demog_tab = st.tabs(['Overview', 'Demographics'])

# Side Bar Options
with st.sidebar:

    sel_charges = st.multiselect('Select Charges',
                                 charges,
                                 on_change=refresh_charts, key='charges')
    sel_county = st.selectbox(
        'Select County', counties, index=1, on_change=refresh_charts, key='county')
    max_results = st.slider('Rank Limit', 2, 71, 10)
with ovv_tab:
    st.markdown('''
                ###
                ''')
    st.altair_chart(ts_line, use_container_width=False)
    st.caption(
        "Select Charges in the sidebar to plot.")
    st.altair_chart(bump)
    st.caption(
        "Adjust the Rank Limit in the side bar to show more counties.")

tot_bar, race_bar, race_off_bar, gbp = col_charts(max_results)
with demog_tab:
    cr_col1, cr_col2, cr_col3 = st.columns(3)

    with cr_col1:
        st.markdown(f"""

                    ## Demographics

                    Black/African Americans **48.56%** and Whites **47.78%** are charges with the vast majority of offenses in Florida. Hispanics come in third with only **3%** of offenses.

                    """)
    with cr_col2:
        st.altair_chart(race_off_bar)
    with cr_col3:
        st.altair_chart(gbp)

    col1, col2 = st.columns([5, 2])

    with col1:
        # st.subheader('County by Offense')
        st.altair_chart(race_bar)
        st.caption(
            "Adjust the Rank Limit in the side bar to show more counties.")

    with col2:
        st.markdown(f"""

                    ## Offenses by County

                    Miami-Dade county has the most offenses and gives some of the longest prison terms.

                    """)
