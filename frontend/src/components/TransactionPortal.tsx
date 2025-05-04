import { useState, useEffect } from "react";

interface Transaction {
  id: string;
  name: string;
  amount: number;
  date: string;
  description: string;
  created_at?: string;
  updated_at?: string;
}

interface TransactionFormData {
  name: string;
  amount: string;
  date: string;
  description: string;
}

// Helper function to format currency
const formatCurrency = (amount: number): string => {
  return amount.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

export default function TransactionPortal() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [formData, setFormData] = useState<TransactionFormData>({
    name: "",
    amount: "",
    date: new Date().toISOString().split("T")[0],
    description: "",
  });

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch("http://localhost:8080/api/transactions", {
        credentials: "include",
      });
      
      if (!response.ok) {
        throw new Error("Failed to fetch transactions");
      }
      
      const data = await response.json();
      // Handle the response format from our backend
      const transactionList = data.transactions || [];
      setTransactions(transactionList);
    } catch (err) {
      setError("Error loading transactions");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    if (name === "amount") {
      // Strip any non-numeric characters except decimal point
      const numericValue = value.replace(/[^0-9.]/g, '');
      setFormData((prev) => ({ ...prev, [name]: numericValue }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const resetForm = () => {
    setFormData({
      name: "",
      amount: "",
      date: new Date().toISOString().split("T")[0],
      description: "",
    });
    setEditingId(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Validate form data
      if (!formData.name || !formData.amount || !formData.date) {
        throw new Error("Name, amount, and date are required");
      }

      const payload = {
        name: formData.name,
        amount: parseFloat(formData.amount),
        date: formData.date,
        description: formData.description,
      };

      let response;

      if (editingId) {
        // Update existing transaction
        response = await fetch(`http://localhost:8080/api/transactions/${editingId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify(payload),
        });
      } else {
        // Create new transaction
        response = await fetch("http://localhost:8080/api/transactions", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify(payload),
        });
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const errorMessage = errorData?.detail || `Failed to ${editingId ? "update" : "create"} transaction`;
        throw new Error(errorMessage);
      }

      // Refresh the transaction list
      await fetchTransactions();
      resetForm();
      setIsFormVisible(false);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred");
      }
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (transaction: Transaction) => {
    setFormData({
      name: transaction.name,
      amount: transaction.amount.toString(),
      date: transaction.date,
      description: transaction.description,
    });
    setEditingId(transaction.id);
    setIsFormVisible(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this transaction?")) {
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8080/api/transactions/${id}`, {
        method: "DELETE",
        credentials: "include",
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const errorMessage = errorData?.detail || "Failed to delete transaction";
        throw new Error(errorMessage);
      }

      await fetchTransactions();
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred");
      }
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <button
          onClick={() => {
            resetForm();
            setIsFormVisible(!isFormVisible);
          }}
          className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
        >
          {isFormVisible ? "Cancel" : "Add Transaction"}
        </button>
      </div>

      {error && (
        <div className="p-3 mb-4 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded">
          {error}
        </div>
      )}

      {isFormVisible && (
        <form onSubmit={handleSubmit} className="mb-6 bg-white dark:bg-gray-800 p-4 rounded shadow">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="name" className="block text-sm font-medium mb-1">
                Transaction Name*
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded dark:bg-gray-700"
                required
              />
            </div>
            <div>
              <label htmlFor="amount" className="block text-sm font-medium mb-1">
                Amount*
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2">$</span>
                <input
                  type="text"
                  id="amount"
                  name="amount"
                  value={formData.amount}
                  onChange={handleInputChange}
                  className="w-full pl-6 px-3 py-2 border border-gray-300 dark:border-gray-700 rounded dark:bg-gray-700"
                  placeholder="0.00"
                  required
                />
              </div>
            </div>
            <div>
              <label htmlFor="date" className="block text-sm font-medium mb-1">
                Date*
              </label>
              <input
                type="date"
                id="date"
                name="date"
                value={formData.date}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded dark:bg-gray-700"
                required
              />
            </div>
            <div className="sm:col-span-2">
              <label htmlFor="description" className="block text-sm font-medium mb-1">
                Description
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded dark:bg-gray-700"
              />
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              {isLoading ? "Processing..." : editingId ? "Update" : "Create"}
            </button>
          </div>
        </form>
      )}

      {isLoading && !isFormVisible ? (
        <div className="text-center py-4">Loading transactions...</div>
      ) : transactions.length === 0 ? (
        <div className="text-center py-4 bg-gray-100 dark:bg-gray-800 rounded">
          No transactions found
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-100 dark:bg-gray-800">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider">Name</th>
                <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider">Amount</th>
                <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider">Date</th>
                <th className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {transactions.map((transaction) => (
                <tr key={transaction.id} className="hover:bg-gray-50 dark:hover:bg-gray-900">
                  <td className="px-4 py-3">
                    <div className="font-medium">{transaction.name}</div>
                    {transaction.description && (
                      <div className="text-sm text-gray-500 truncate max-w-xs">
                        {transaction.description}
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    ${formatCurrency(transaction.amount)}
                  </td>
                  <td className="px-4 py-3">
                    {new Date(transaction.date).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEdit(transaction)}
                        className="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-xs"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(transaction.id)}
                        className="px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-xs"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
} 