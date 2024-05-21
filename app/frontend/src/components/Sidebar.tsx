import React, { useState, useEffect } from 'react';

import trashIcon from '../img/trash.svg';
import plusIcon from '../img/plus.svg';

import Loader from './Loader';
import ErrorMsg from './ErrorMsg';

import * as homeService from '../services/home';
import { UserSettings } from '../services/home';

interface SidebarProps {
    onFileUpload: (file: File) => void;
}

interface Document {
    id: string;
    name: string;
}

const Sidebar: React.FC<SidebarProps> = () => {
    const [list, setList] = useState<Document[]>([]);
    const [showLoader, setShowLoader] = useState(false);
    const [noDocuments, setNoDocuments] = useState(false);
    const [serverDown, setServerDown] = useState(false);
    const [wrongFiletype, setWrongFiletype] = useState(false);
    const [selectedModel, setSelectedModel] = useState('gpt-4-32k'); // Default value

    useEffect(() => {
        homeService
            .getDocuments()
            .then((response) => {
                setWrongFiletype(false);
                const data = response.data;
                const documents: Document[] = data.map(
                    (item: { id: string; name: string }) => ({
                        id: item.id,
                        name: item.name,
                    })
                );
                setList(documents);
                if (documents.length == 0) {
                    setNoDocuments(true);
                }
            })
            .catch((error) => {
                console.error('Error fetching data:', error);
                setServerDown(true);
            });
    }, []);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target?.files?.[0];
        setNoDocuments(false);
        setShowLoader(true);
        if (file) {
            try {
                await homeService.uploadFile(file).then((response) => {
                    setShowLoader(false);
                    setList((prevList) => [
                        ...prevList,
                        { id: response.data, name: file.name },
                    ]);
                });
            } catch (error) {
                setShowLoader(false);
                setWrongFiletype(true);
                setTimeout(() => {
                    setWrongFiletype(false);
                }, 5000);
                console.error('Error uploading file:', error);
            }
        }
    };

    const handleRemoveItem = (index: number) => {
        const itemID = list[index].id;
        homeService.deleteDocument(itemID).then(() => {
            setList((prevList) => {
                const updatedList = prevList.filter((_, i) => i !== index);

                if (updatedList.length === 0) {
                    setNoDocuments(true);
                }

                return updatedList;
            });
        });
    };

    const handleModelChange = async (
        e: React.ChangeEvent<HTMLSelectElement>
    ) => {
        const selectedModel = e.target.value;
        setSelectedModel(selectedModel);

        const settings: UserSettings = { llm_model_name: selectedModel };

        try {
            await homeService.updateUserSettings(settings);
        } catch (error) {
            console.error('Error updating user settings:', error);
        }
    };

    return (
        <aside className="p-4 border-r w-1/3">
            <div className="flex items-center mb-4">
                <h2 className="text-xl mr-4">Your documents</h2>
                <label htmlFor="fileInput" className="cursor-pointer">
                    <img src={plusIcon} className="w-6 h-6" />
                    <input
                        id="fileInput"
                        type="file"
                        accept=".pdf"
                        onChange={handleFileUpload}
                        className="hidden"
                    />
                </label>
            </div>

            <div className="mb-4">
                <label htmlFor="modelSelect" className="block mb-2">
                    Select Model:
                </label>
                <select
                    id="modelSelect"
                    value={selectedModel}
                    onChange={handleModelChange}
                    className="block w-full p-2 border border-gray-300 rounded"
                >
                    <option value="gpt-3.5">gpt-3.5</option>
                    <option value="gpt-4-32k">gpt-4</option>
                </select>
            </div>

            {noDocuments && (
                <ErrorMsg
                    message="You have no documents yet. Start by uploading a first one by clicking on plus icon above."
                    type="info"
                />
            )}

            {wrongFiletype && (
                <ErrorMsg
                    message="Filetype not supported, try another file (PDF, no OCR)."
                    type="danger"
                />
            )}
            {serverDown && (
                <ErrorMsg
                    message="Server is currently unavailable. Please try again later."
                    type="danger"
                />
            )}

            {showLoader && (
                <Loader message="Your upload is being processed..." />
            )}

            <ul className="mt-12">
                {list.map((item, index) => (
                    <li
                        key={index}
                        className="flex justify-between items-center mb-6"
                    >
                        <div className="break-all">{item.name}</div>
                        <button
                            onClick={() => handleRemoveItem(index)}
                            className="flex items-center justify-end w-12 h-12"
                        >
                            <img
                                src={trashIcon}
                                className="w-5 h-5"
                                alt="Delete"
                            />
                        </button>
                    </li>
                ))}
            </ul>
        </aside>
    );
};

export default Sidebar;
