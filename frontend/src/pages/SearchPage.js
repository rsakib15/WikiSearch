import React from "react";
import { Link } from "react-router-dom";
import { useStateValue } from "../store/StateProvider";
import useGoogleSearch from "../components/useGoogleSearch";
import Search from "../components/Search";
import SearchIcon from "@material-ui/icons/Search";
import DescriptionIcon from "@material-ui/icons/Description";
import ImageIcon from "@material-ui/icons/Image";
import RoomIcon from "@material-ui/icons/Room";

function SearchPage() {
    const [{ term }, dispatch] = useStateValue();
    const { data } = useGoogleSearch(term);

    console.log(data);
    console.log(term);

    return (
        <div className="searchPage">
            <div className="searchPage__header">
                <Link to="/">
                    <img src={'logo.svg'} className="wikisearch-logo-small" alt="wikisearh-logo"/>
                </Link>

                <div className="searchPage__headerBody">
                    <Search hideButtons/>

                    {term &&
                        <div>
                            <p className="searchPage__resultCount">
                                About {data?.searchInformation.formattedTotalResults} results (
                                {data?.searchInformation.formattedSearchTime} seconds) for {term}
                            </p>
                        </div>
                    }
                </div>

            </div>

            {term && (
                <div className="searchPage__results">
                    {data?.items.map((item) => (
                        <div className="searchPage__result">
                            <a className="searchPage__resultTitle" href={item.link}>
                                <h2>{item.title}</h2>
                            </a>
                            <p className="searchPage__resultSnippet">{item.snippet}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default SearchPage;