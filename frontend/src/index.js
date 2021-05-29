import React from "react";
import ReactDOM from "react-dom";
import App from "./components/App";
import reducer, { initialState } from "./store/reducer";
import { StateProvider } from "./store/StateProvider";
import "./styles/index.css";

ReactDOM.render(
    <StateProvider initialState={initialState} reducer={reducer}>
        <App />
    </StateProvider>,
    document.getElementById("root")
);