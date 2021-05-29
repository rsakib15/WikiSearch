import React, { createContext, useContext, useReducer } from "react";

// Preparing data layer / Menyediakan data
export const StateContext = createContext();

// initialState is about what the data is look like first time
// childrens is the <App/>

// Hihger order component
export const StateProvider = ({ reducer, initialState, children }) => (
    <StateContext.Provider value={useReducer(reducer, initialState)}>
        {children}
    </StateContext.Provider>
);

// Hook to pull informations from data layer
export const useStateValue = () => useContext(StateContext);