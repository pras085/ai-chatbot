import Sidebar from "../../components/Sidebar";
import React, { useState, useEffect } from "react";
import KnowledgeBaseList from "../../components/KnowledgeBaseList";
import { useNavigate } from "react-router-dom";
import { fetchAllKnowledges } from "../../services/api";

function AdminKnowledgeBasePage() {
    const [knowledges, setKnowledgeBase] = useState([]);
    const [isReloading, setIsReloading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        // check username
        if (localStorage.getItem("username") !== "superadmin") {
            navigate("/")
        }
        
        // wrap fetchRules async to separate function
        const fetchKnowledges = async () => {
            const data = await fetchAllKnowledges();
            console.log(data);
            setKnowledgeBase(data);
        }
        
        fetchKnowledges();
        setIsReloading(false);
    }, [isReloading, navigate])

    return (
        <>
            <div className="flex h-[90vh]">
                <Sidebar />

                {/* Main Content */}
                <main className="flex-1 p-6">
                    <h1 className="text-2xl mb-4">Admin Knowledge Base Page</h1>
                    <KnowledgeBaseList knowledges={knowledges} setIsReloading={setIsReloading}/>
                </main>
            </div>
        </>
    )
};

export default AdminKnowledgeBasePage;