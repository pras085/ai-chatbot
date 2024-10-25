import React, { useState } from 'react';
import Editor from 'react-simple-wysiwyg';
import { updateRule } from '../services/api';

const Modal = ({isOpen, toggleModal, feature, rule, onChangeRule, saveUpdate}) => {
    return (
      <div>
        {/* Modal */}
        {isOpen && (
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
            <div className="bg-white rounded-lg shadow-lg max-w-6xl w-full h-auto p-8 relative">
              {/* Tombol Close */}
              <button
                onClick={toggleModal}
                className="absolute top-2 right-2 text-gray-600 hover:text-gray-900"
              >
                ✖
              </button>
              
              {/* Modal Title */}
              <h2 className="text-2xl font-semibold mb-4">{feature}</h2>
  
              {/* WYSIWYG Editor */}
              <div className="mb-4">
                <Editor style={{ textAlign: 'left' }} value={rule} onChange={(event) => onChangeRule(event.target.value || '')}/>
              </div>
  
              {/* Buttons Section */}
              <div className="flex justify-end space-x-2">
                <button
                  onClick={toggleModal}
                  className="bg-red-500 text-white px-4 py-2 rounded"
                >
                  Close
                </button>
                <button
                  onClick={saveUpdate}
                  className="bg-blue-500 text-white px-4 py-2 rounded"
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };  

const RulesList = ({ data = [] }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [selectedRule, setSelectedRule] = useState('');
    const [selectedFeature, setSelectedFeature] = useState(null);

    const handleEdit = (rule, feature) => {
      setSelectedRule(rule || ''); // Jika rule null, set string kosong
      setSelectedFeature(feature);
      setIsOpen(true);
    };

    const handleUpdate = () => {
      setIsOpen(false);

      console.log('Selected Rule:', selectedRule);
      console.log('Selected Feature:', selectedFeature);
      
      
    //   Simpan perubahan pada rule dan feature
      const update = async () => {
          const response = await updateRule(selectedFeature, selectedRule);

          if (response.status === 200) {
              window.location.reload();
          }
      }

      update();
    };

    return (
        <>
            <Modal isOpen={isOpen} toggleModal={() => setIsOpen(false)} feature={selectedFeature} rule={selectedRule} onChangeRule={setSelectedRule} saveUpdate={handleUpdate}/>
            <div className="flex justify-center mt-10">
                <table className="table-auto border-collapse border border-gray-200 w-full">
                <thead>
                    <tr>
                    <th className="border border-gray-300 px-4 py-2">No</th>
                    <th className="border border-gray-300 px-4 py-2">Feature</th>
                    <th className="border border-gray-300 px-4 py-2">Created At</th>
                    <th className="border border-gray-300 px-4 py-2">Updated At</th>
                    <th className="border border-gray-300 px-4 py-2">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((rules, no) => (
                    <tr key={rules.id}>
                        <td className="border border-gray-300 px-4 py-2 text-center">{no + 1}</td>
                        <td className="border border-gray-300 px-4 py-2 text-left">{rules.feature}</td>
                        <td className="border border-gray-300 px-4 py-2">{rules.created_at}</td>
                        <td className="border border-gray-300 px-4 py-2">{rules.updated_at}</td>
                        <td className="border border-gray-300 px-4 py-2">
                            <div style={{ display: 'flex' , flexDirection: 'row'}}>
                                <button className="bg-blue-500 text-white px-4 py-1 rounded mr-2" onClick={() => handleEdit(rules.rule, rules.feature)}>Edit</button>
                            </div>
                        </td>
                    </tr>
                    ))}
                </tbody>
                </table>
            </div>
      </>

    );
  };

export default RulesList;
