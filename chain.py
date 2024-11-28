import streamlit as st
import pandas as pd
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value

st.title('Supply Chain Optimization Tool')

st.header('Input Data')

# Number of suppliers and customers
num_suppliers = st.number_input('Enter the number of suppliers', min_value=1, value=2, step=1)
num_customers = st.number_input('Enter the number of customers', min_value=1, value=2, step=1)

# Names of suppliers and customers
supplier_names = ['Supplier_' + str(i+1) for i in range(int(num_suppliers))]
customer_names = ['Customer_' + str(j+1) for j in range(int(num_customers))]

# Input supply capacities
st.subheader('Supply Capacities')
supply_data = {}
for supplier in supplier_names:
    supply = st.number_input(f'Supply capacity of {supplier}', min_value=0.0, value=100.0, key=supplier)
    supply_data[supplier] = supply

# Input demand requirements
st.subheader('Demand Requirements')
demand_data = {}
for customer in customer_names:
    demand = st.number_input(f'Demand requirement of {customer}', min_value=0.0, value=50.0, key=customer)
    demand_data[customer] = demand

# Input transportation costs
st.subheader('Transportation Costs')
cost_data = pd.DataFrame(columns=customer_names, index=supplier_names)

for supplier in supplier_names:
    for customer in customer_names:
        cost = st.number_input(f'Cost from {supplier} to {customer}', min_value=0.0, value=1.0, key=(supplier, customer))
        cost_data.loc[supplier, customer] = cost

# Button to run optimization
if st.button('Run Optimization'):
    # Build the optimization model
    prob = LpProblem("Transportation_Problem", LpMinimize)

    # Decision variables
    routes = [(s, c) for s in supplier_names for c in customer_names]
    vars = LpVariable.dicts("Route", (supplier_names, customer_names), lowBound=0, cat='Continuous')

    # Objective function
    prob += lpSum([vars[s][c]*cost_data.loc[s, c] for (s, c) in routes]), "Total Transportation Cost"

    # Supply constraints
    for s in supplier_names:
        prob += lpSum([vars[s][c] for c in customer_names]) <= supply_data[s], f"Supply_{s}"

    # Demand constraints
    for c in customer_names:
        prob += lpSum([vars[s][c] for s in supplier_names]) >= demand_data[c], f"Demand_{c}"

    # Solve the problem
    prob.solve()

    # Output results
    st.subheader('Optimization Results')
    st.write(f'Status: {LpStatus[prob.status]}')
    st.write(f'Total Transportation Cost: {value(prob.objective)}')

    # Create a dataframe to display the results
    result_data = pd.DataFrame(0.0, index=supplier_names, columns=customer_names)
    for s in supplier_names:
        for c in customer_names:
            result_data.loc[s, c] = vars[s][c].varValue

    st.write('Optimal Transportation Plan:')
    st.dataframe(result_data)
