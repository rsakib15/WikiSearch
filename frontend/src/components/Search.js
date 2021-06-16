import React, {useState} from "react";
import {Button} from "@material-ui/core";
import {useHistory} from "react-router-dom";
import {useStateValue} from "../store/StateProvider";
import {actionTypes} from "../store/reducer";
import Autosuggest from 'react-autosuggest';
import axios from 'axios';

export default function Search({ hideButtons = false }) {
    const [{ data }, dispatch] = useStateValue();
    const [input, setInput] = useState("");
    const [value, setValue] = useState("");
    const [suggestions, setSuggestions] = useState([]);
    const [rank, setRank] = useState("cosine");
    const history = useHistory();
    // const q = this.location.q;
    //
    //
    // setValue(q)

    const search = () => {
        console.log("search called")
        if(value==="") {
            console.log("No value")
            return
        }
        dispatch({
            type: actionTypes.SET_SEARCH_TERM,
            term: value,
            method: rank
        });
        history.push('/search?q='+ value + "&m="  + rank)
    };

    const d = async (inputValue) => {
        axios.get(`http://127.0.0.1:5000/suggestion?&q=${inputValue}`,
            {
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'X-Requested-With',
                    'Content-Type': 'application/json'
                }
            }).then(function (response) {
            setSuggestions(response.data.result)
        });
    };

    const getSuggestions = value => {
        const inputValue = value.trim().toLowerCase();
        return d(inputValue)
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

    const getSuggestionValue = suggestion => suggestion;
    const renderSuggestion = suggestion => (
        <div>
            {suggestion}
        </div>
    );

    const onKeyDown = (event) => {
        switch (event.keyCode) {
            case 13: {
                event.preventDefault();
                search()
            }
        }
    };

    const inputProps = {
        placeholder: 'Search',
        value,
        onChange: onChange,
    };

    const rankChanged = (e) =>{
        console.log(e.target.value)
        setRank(e.target.value)
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

                {
                    <div className="search__buttons">
                        <Button type="submit" onClick={search} variant="outlined">Search</Button>
                    </div>
                }
                <div className="ranking">
                    <span><input type="radio" name="site_name" value="bow" checked={rank==="bow"} onChange={rankChanged}/> BOW</span>
                    <span><input type="radio" name="site_name" value="jaccard" checked={rank==="jaccard"} onChange={rankChanged}/> Jaccard</span>
                    <span><input type="radio" name="site_name" value="tfidf" checked={rank==="tfidf"} onChange={rankChanged}/> TF_IDF</span>
                    <span><input type="radio" name="site_name" value="highidf" checked={rank==="highidf"} onChange={rankChanged}/> HIGH_IDF</span>
                    <span><input type="radio" name="site_name" value="cosine" checked={rank==="cosine"} onChange={rankChanged}/> Cosine</span>
                </div>
            </div>
        </div>
    );
}