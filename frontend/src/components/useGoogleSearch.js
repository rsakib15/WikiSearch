import { useState, useEffect } from "react";

export default function useGoogleSearch(term, method) {
    const [data, setData] = useState(null);

    useEffect(() => {
        if(term == null){
            return
        }
        const fetchData = async () => {
            fetch(`http://127.0.0.1:5000/search?&q=${term}&m=${method}`)
                .then((response) => response.json())
                .then((result) => {
                    console.log(result)
                    setData(result);
                });
        };

        fetchData();
    }, [term,method]);
    return { data };
}