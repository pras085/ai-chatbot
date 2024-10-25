import { useEffect, useState } from "react";
import { getRuleByFeature } from "../services/api";
export default function CodeCheckDetail({feature}) {
    const [rule, setRule] = useState('');

    useEffect(() => {
        getRuleById();
    }, [feature]);
    
    const getRuleById = () => {
        const getRule = async () => {
            const response = await getRuleByFeature(feature);
            console.log(response);
            setRule(response.rule);
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
            
            <div class="p-4 h-full">
                <div
                dangerouslySetInnerHTML={{ __html: rule }}
                />
            </div>
            <div class="mx-3 border-t border-slate-200 pb-3 pt-2 px-1">
                <span class="text-sm text-slate-600 font-medium">
                Last updated: 4 hours ago
                </span>
            </div>
        </div>
    )
}