import React, { useState } from "react";
import SearchIcon from "@material-ui/icons/Search";
import MicIcon from "@material-ui/icons/Mic";
import { Button } from "@material-ui/core";
import { useHistory } from "react-router-dom";
import { useStateValue } from "../store/StateProvider";
import { actionTypes } from "../store/reducer";
import Autosuggest from 'react-autosuggest';

export default function Search({ hideButtons = false }) {
    const [{ data }, dispatch] = useStateValue();
    const [input, setInput] = useState("");
    const [value, setValue] = useState("");
    const [suggestions, setSuggestions] = useState([]);
    const history = useHistory();

    const search = () => {
        dispatch({
            type: actionTypes.SET_SEARCH_TERM,
            term: value,
        });
        history.push("/search");
    };

    const languages = [
        {name: 'C', year: 1972},
        {name: 'Elm', year: 2012},
        {name: 'Ema', year: 2012},
    ];

    const getSuggestions = value => {
        const inputValue = value.trim().toLowerCase();
        const inputLength = inputValue.length;

        return inputLength === 0 ? [] : languages.filter(lang =>
            lang.name.toLowerCase().slice(0, inputLength) === inputValue
        );
    };

    const onChange = (event, { newValue }) => {
        setValue(newValue)
    };

    const onSuggestionsFetchRequested = ({ value }) => {
        setSuggestions(getSuggestions(value))
    };

    const onSuggestionsClearRequested = () => {
        setSuggestions([])
    };

    const getSuggestionValue = suggestion => suggestion.name;
    const renderSuggestion = suggestion => (
        <div>
            {suggestion.name}
        </div>
    );

    const onKeyDown = (event) => {
        switch (event.keyCode) {
            case 13: {
                event.preventDefault();
                console.log("oyeeeeee")
                search()
            }
        }
    };

    const inputProps = {
        placeholder: 'Search',
        value,
        onChange: onChange,
        onKeyDown: onKeyDown
    };


    return (
        <div>
            <div className="autosuggest-search">
                <Autosuggest
                    suggestions={suggestions}
                    onSuggestionsFetchRequested={onSuggestionsFetchRequested}
                    onSuggestionsClearRequested={onSuggestionsClearRequested}
                    getSuggestionValue={getSuggestionValue}
                    renderSuggestion={renderSuggestion}
                    inputProps={inputProps}
                />

                {!hideButtons &&
                    <div className="search__buttons">
                        <Button type="submit" onClick={search} variant="outlined">Search</Button>
                    </div>
                }
            </div>
        </div>
    );
}