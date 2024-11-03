import Sidebar from "../components/Sidebar";

function AdminUserManagementPage() {
    return (
        <>
            <div className="flex h-[90vh]">
                <Sidebar />

                {/* Main Content */}
                <main className="flex-1 p-6">
                    <h1 className="text-2xl mb-4">Admin User Management Base Page</h1>
                </main>
            </div>
        </>
    )
};

export default AdminUserManagementPage;