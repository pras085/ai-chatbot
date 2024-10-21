import React, { useState, useCallback, useRef, useEffect } from "react";
import RulesList from "../components/RulesList";
import { fetchAllRules } from "../services/api";


function AdminPage() {
    const [rules, setRules] = useState([]);

    useEffect(() => {
        // wrap fetchRules async to separate function
        const fetchRules = async () => {
            const data = await fetchAllRules();
            console.log(data);
            
            setRules(data);
        }
        fetchRules();
    }, []);
    
    return <>
        <div className="container" style={{ textAlign: "center" }}>
            <h2 className="text-3xl font-semibold">Code Check Rules</h2>
            <RulesList data={rules}/>
        </div>
    </>;
}

export default AdminPage;