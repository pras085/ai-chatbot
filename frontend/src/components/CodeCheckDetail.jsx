import { useEffect, useState } from "react";
import { getRuleByFeature } from "../services/api";
export default function CodeCheckDetail({feature}) {
    const [rule, setRule] = useState('');
    const [updated_at, setUpdated_at] = useState('');

    useEffect(() => {
        getRuleById();
    }, [feature]);
    
    const getRuleById = () => {
        const getRule = async () => {
            const response = await getRuleByFeature(feature);
            console.log(response);
            setRule(response.rule);
            setUpdated_at(response.updated_at);
        }
        getRule();
    }
    return (
        <div class="relative flex flex-col bg-white shadow-sm border border-slate-200 rounded-lg w-full h-full">      
            <div class="mx-3 mb-0 border-b border-slate-200 pt-3 pb-2 px-1">
                <span class="text-sm font-medium text-slate-600">
                {`Rules ${feature}`}
                </span>
            </div>
            
             {/* Scrollable Content */}
             <div className="p-4 overflow-y-auto h-full scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
                <div
                    className="prose prose-sm max-w-none"
                    dangerouslySetInnerHTML={{ __html: rule }}
                />
            </div>

            <div class="mx-3 border-t border-slate-200 pb-3 pt-2 px-1">
                <span class="text-sm text-slate-600 font-medium">
                Last updated: {new Date(updated_at).toDateString()}
                </span>
            </div>
        </div>
    )
}