import React, { useState } from 'react';
import Editor from 'react-simple-wysiwyg';
import { updateRule } from '../services/api';
import { Clock, Edit2 } from 'lucide-react';

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
            <div className="p-6">
              <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-gray-50 border-b border-gray-200">
                        <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                          No
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                          Feature
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                          Created At
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                          Updated At
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                          Action
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {data.map((rule, index) => (
                        <tr 
                          key={rule.id}
                          className="hover:bg-gray-50 transition-colors duration-200"
                        >
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {index + 1}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                                {rule.feature}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <div className="flex items-center">
                              <Clock className="w-4 h-4 mr-2 text-gray-400" />
                              {new Date(rule.created_at).toLocaleString()}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <div className="flex items-center">
                              <Clock className="w-4 h-4 mr-2 text-gray-400" />
                              {new Date(rule.updated_at).toLocaleString()}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button className="inline-flex items-center px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-md transition-colors duration-200" onClick={() => handleEdit(rule.rule, rule.feature)}>
                              <Edit2 className="w-4 h-4 mr-1" />
                              Edit
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
      </>

    );
  };

export default RulesList;
