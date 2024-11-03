import Sidebar from "../../components/Sidebar";
import React, { useState, useEffect } from "react";
import RulesList from "../../components/RulesList";
import { fetchAllRules } from "../../services/api";
import { useNavigate } from "react-router-dom";

function AdminCodeCheckRulesPage() {
    
    const [rules, setRules] = useState([]);
    const [isReloading, setIsReloading] = useState(false);
    const navigate = useNavigate();


    useEffect(() => {
        // check username
        if (localStorage.getItem("username") !== "superadmin") {
            navigate("/")
        }
        
        // wrap fetchRules async to separate function
        const fetchRules = async () => {
            const data = await fetchAllRules();
            console.log(data);
            setRules(data);
        }

        fetchRules();
        setIsReloading(false);
    }, [isReloading, navigate]);
    

    return (
        <>
            <div className="flex h-[90vh]">
                <Sidebar />
                {/* Main Content */}
                <main className="flex-1 p-6">
                    <h1 className="text-2xl mb-4">Admin Code Check Rules</h1>
                    <RulesList data={rules}/>
                </main>
            </div>
        </>
    )
};

export default AdminCodeCheckRulesPage;