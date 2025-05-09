import { useState } from "react";

export default function WristbandTestComponents() {
  const [response, setResponse] = useState<string | null>(null);

  const handleTestDecryptCookie = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/test_decrypt_cookie`, {
        method: "GET",
        credentials: "include", // Include cookies in the request
      });

      if (!res.ok) {
        throw new Error("Failed to fetch");
      }

      const data = await res.text();
      setResponse(data);
    } catch (error) {
      console.error("Error:", error);
      setResponse("Error fetching data");
    }
  };

  return (
    <div className="flex flex-col gap-2 w-full">
      <button
        onClick={handleTestDecryptCookie}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Test Decrypt Cookie
      </button>
     
      {response && (
        <div className="mt-4 rounded border border-gray-300 dark:border-gray-700">
          <div className="bg-gray-100 dark:bg-gray-800 p-2 border-b border-gray-300 dark:border-gray-700">
            <p className="font-bold text-sm">Response:</p>
          </div>
          <div className="p-2 max-h-60 overflow-auto">
            <pre className="text-xs whitespace-pre-wrap break-all">{
              (() => {
                try {
                  if (typeof response === 'string') {
                    // Try to parse as JSON first
                    const parsed = JSON.parse(response);
                    return JSON.stringify(parsed, null, 2);
                  }
                  return JSON.stringify(response, null, 2);
                } catch (e) {
                  // If not valid JSON, just show as string
                  return response;
                }
              })()
            }</pre>
          </div>
        </div>
      )}



    </div>
  );
} 