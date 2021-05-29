import { useState, useEffect } from "react";

export default function useGoogleSearch(term) {
    const [data, setData] = useState(null);
    useEffect(() => {
        const fetchData = async () => {
            fetch(`http://127.0.0.1:5000/search?&q=${term}`)
                .then((response) => response.json())
                .then((result) => {
                    setData(result);
                });
        };

        fetchData();
    }, [term]);
    return { data };
}