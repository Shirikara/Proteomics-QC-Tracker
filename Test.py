# Test script to check Proteomics_QC_Tracker.py functions
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import unittest
from unittest.mock import patch


# Main functions
def extract_hela_amount(filename):
    match = re.search(r'Hela(\d+)', filename)
    if match:
        return int(match.group(1))
    return None


def process_folder(folder_path):
    data = []
    for file in os.listdir(folder_path):
        if file.endswith('.d'):
            hela_amount = extract_hela_amount(file)
            if hela_amount is not None:
                data.append({'Filename': file, 'HeLa_Amount': hela_amount})

    qc_df = pd.DataFrame(data)
    if not qc_df.empty:
        output_path = os.path.join(folder_path, 'HeLa_QC_Database.csv')
        qc_df.to_csv(output_path, index=False)
        print(f"QC Database saved to {output_path}")
    return qc_df


def plot_hela_qc_data(qc_df):
    if qc_df.empty:
        raise ValueError("QC DataFrame is empty. Cannot plot data.")
    qc_df.plot(x='Filename', y='HeLa_Amount', kind='bar', legend=False, figsize=(10, 6))
    plt.xlabel('Filename')
    plt.ylabel('HeLa Amount')
    plt.title('HeLa QC Data')
    plt.tight_layout()
    plt.show()


# GUI
def hela_qc_tracker():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Folder with HeLa QC Files")
    if not folder_path:
        print("No folder selected. Exiting.")
        return

    qc_df = process_folder(folder_path)
    if not qc_df.empty:
        plot_hela_qc_data(qc_df)
    else:
        print("No HeLa data found in the selected folder.")


# Unit Tests
class TestHeLaQCTracker(unittest.TestCase):
    def test_extract_hela_amount_valid(self):
        self.assertEqual(extract_hela_amount("Hela200.d"), 200)
        self.assertEqual(extract_hela_amount("test_Hela100.d"), 100)

    def test_extract_hela_amount_invalid(self):
        self.assertIsNone(extract_hela_amount("sample.d"))
        self.assertIsNone(extract_hela_amount("HelaXX.d"))

    @patch('os.listdir')
    def test_process_folder(self, mock_listdir):
        mock_listdir.return_value = ['Hela200.d', 'Hela100.d', 'invalid_file.txt']
        folder_path = '/fake/path'
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            qc_df = process_folder(folder_path)
            self.assertEqual(len(qc_df), 2)
            self.assertIn('Filename', qc_df.columns)
            self.assertIn('HeLa_Amount', qc_df.columns)
            mock_to_csv.assert_called_once_with(os.path.join(folder_path, 'HeLa_QC_Database.csv'), index=False)

    @patch('matplotlib.pyplot.show')
    def test_plot_hela_qc_data(self, mock_show):
        sample_data = {'Filename': ['Hela200.d', 'Hela100.d'], 'HeLa_Amount': [200, 100]}
        qc_df = pd.DataFrame(sample_data)
        plot_hela_qc_data(qc_df)
        mock_show.assert_called_once()

    def test_plot_hela_qc_data_empty(self):
        empty_df = pd.DataFrame(columns=['Filename', 'HeLa_Amount'])
        with self.assertRaises(ValueError):
            plot_hela_qc_data(empty_df)


# Run Unit Tests
if __name__ == "__main__":
    unittest.main()
