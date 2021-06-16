import React, { useState,useEffect } from "react";
import { Link } from "react-router-dom";
import { useStateValue } from "../store/StateProvider";
import useGoogleSearch from "../components/useGoogleSearch";
import Search from "../components/Search";

function SearchPage() {
    const [{ term, method }, dispatch] = useStateValue();
    const { data } = useGoogleSearch(term, method)

    return (
        <div className="searchPage">
            <div className="searchPage__header">
                <Link to="/">
                    <img src={'logo.svg'} className="wikisearch-logo-small" alt="wikisearh-logo"/>
                </Link>

                <div className="searchPage__headerBody">
                    <Search hideButtons/>

                    {term && data?.result.length>0 &&
                        <div>
                            <p className="searchPage__resultCount">
                                About {data?.result.length} results (
                                {data?.elapsed_time} seconds) for {term}
                            </p>
                        </div>
                    }
                </div>
            </div>

            {term && (
                <div className="searchPage__results">
                    {
                        data?.result.length===0 && <div className="searchPage__result">No Result Found</div>
                    }
                    {data?.result.length>0 && data?.result.map((item) => (
                        <div className="searchPage__result">
                            <a className="searchPage__resultTitle" href={item.url} target="_blank" ><h2>{item.title}</h2></a>
                            <div>
                                <p className="searchPage__resultSnippet">{item.url}</p>
                            </div>
                            <div className="searchPage__text">
                                <p>{item.text}</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default SearchPage;