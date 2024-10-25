import React, { useState } from 'react';
import { createKnowledge, deleteKnowledge } from '../services/api';

const Modal = ({isOpen, toggleModal, setIsReloading}) => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleSubmit = (event) => {
    const create = async () => {
      const result = await createKnowledge(question, answer);
      alert('Success');
      // Reset form
      setQuestion('');
      setAnswer('');
      // Tutup modal
      toggleModal();
      setIsReloading(true);
    }
    event.preventDefault();
    if (question && answer) {
      create();
    } else {
      alert('Error creating knowledge');  
    }
  };
    return (
      <div>
        {/* Modal */}
        {isOpen && (
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
            <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full h-auto p-8 relative">
              {/* Tombol Close */}
              <button
                onClick={toggleModal}
                className="absolute top-2 right-2 text-gray-600 hover:text-gray-900"
              >
                ✖
              </button>
              
              {/* Modal Title */}
              <h2 className="text-2xl font-semibold mb-4">Add New Rule</h2>
  
              {/* Form Section */}
              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2">Question</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                  placeholder="Enter question"
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                />
              </div>
              <div className="mb-4">
                <label className="block text-gray-700 font-bold mb-2">Answer</label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                  placeholder="Enter answer"
                  value={answer}
                  onChange={(event) => setAnswer(event.target.value)}
                ></textarea>
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
                  onClick={(event) => handleSubmit(event)}
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

const KnowledgeBaseList = ({knowledges, setIsReloading}) => {
    const [isOpen, setIsOpen] = useState(false);

    const handleDelete = (id) => {
      const deleteKnowledgeById = async () => {
        const response = await deleteKnowledge(id);
        console.log(response);
        alert('Success');
        setIsReloading(true);
      }

      deleteKnowledgeById();
    }
    return (
        <>
            <Modal isOpen={isOpen} toggleModal={() => setIsOpen(false)} setIsReloading={setIsReloading}/>
            <div className="flex mt-1 justify-end">
                <button className="bg-green-500 text-white px-4 py-1 rounded" onClick={() => setIsOpen(true)}>Create</button>
            </div>
            <div className="flex justify-center mt-2">
                <table className="table-auto border-collapse border border-gray-200 w-full">
                <thead>
                    <tr>
                    <th className="border border-gray-300 px-4 py-2">No</th>
                    <th className="border border-gray-300 px-4 py-2">Question</th>
                    <th className="border border-gray-300 px-4 py-2">Answer</th>
                    <th className="border border-gray-300 px-4 py-2">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {knowledges.map((knowledge, no) => (
                    <tr key={knowledge.id}>
                        <td className="border border-gray-300 px-4 py-2 text-center">{no + 1}</td>
                        <td className="border border-gray-300 px-4 py-2 text-left">{knowledge.question}</td>
                        <td className="border border-gray-300 px-4 py-2 text-left">{knowledge.answer}</td>
                        <td className="border border-gray-300 px-4 py-2">
                            <div style={{ display: 'flex' , flexDirection: 'row'}}>
                                <button className="bg-blue-500 text-white px-4 py-1 rounded mr-2" onClick={() => alert('ok')}>Edit</button>
                                <button className="bg-red-500 text-white px-4 py-1 rounded mr-2" onClick={() => handleDelete(knowledge.id)}>Delete</button>
                            </div>
                        </td>
                    </tr>
                    ))}
                </tbody>
                </table>
            </div>
        </>
    );
}

export default KnowledgeBaseList;