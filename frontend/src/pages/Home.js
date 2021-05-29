import React from "react";
import Search from "../components/Search";

function Home() {
    return (
        <div className="home container">
            <div className="home__body">
                <header className="wikisearch-logo-area">
                    <img src={'logo.svg'} className="wikisearch-logo" alt="wikisearh-logo"/>
                </header>
                <div className="home__inputContainer">
                    <Search />
                </div>
            </div>
        </div>
    );
}

export default Home;