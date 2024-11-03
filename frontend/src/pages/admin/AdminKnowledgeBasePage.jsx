import Sidebar from "../../components/Sidebar";

function AdminKnowledgeBasePage() {
    return (
        <>
            <div className="flex h-[90vh]">
                <Sidebar />

                {/* Main Content */}
                <main className="flex-1 p-6">
                    <h1 className="text-2xl mb-4">Admin Knowledge Base Page</h1>
                </main>
            </div>
        </>
    )
};

export default AdminKnowledgeBasePage;