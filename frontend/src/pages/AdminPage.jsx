import React, { useState, useEffect } from "react";
import RulesList from "../components/RulesList";
import { fetchAllRules, fetchAllKnowledges } from "../services/api";
import KnowledgeBaseList from "../components/KnowledgeBaseList";


function AdminPage() {
    const [rules, setRules] = useState([]);
    const [knowledges, setKnowledgeBase] = useState([]);

    useEffect(() => {
        // wrap fetchRules async to separate function
        const fetchRules = async () => {
            const data = await fetchAllRules();
            console.log(data);
            setRules(data);
        }

        const fetchKnowledges = async () => {
            const data = await fetchAllKnowledges();
            console.log(data);
            setKnowledgeBase(data);
        }
        
        fetchRules();
        fetchKnowledges();
    }, []);
    
    return <>
        <div className="w-full p-8" style={{ textAlign: "center" }}>
            <h2 className="text-3xl font-semibold">Code Check Rules</h2>
            <RulesList data={rules}/>

            <h2 className="text-3xl font-semibold mt-10">Knowledge Base</h2>
            <KnowledgeBaseList knowledges={knowledges} />
        </div>
    </>;
}

export default AdminPage;