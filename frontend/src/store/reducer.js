export const initialState = {
    term: null,
};

//Whenever data comes from search bar, we need to dispatch it
export const actionTypes = {
    SET_SEARCH_TERM: "SET_SEARCH_TERM",
};

// state of data and action of search bar
// listening to any dispatch action
const reducer = (state, action) => {
    // any data manipulation will informed on log
    console.log(action);

    switch (action.type) {
        case actionTypes.SET_SEARCH_TERM:
            return {
                ...state,
                term: action.term,
                method: action.method
            };
        default:
            return state;
    }
};

export default reducer;