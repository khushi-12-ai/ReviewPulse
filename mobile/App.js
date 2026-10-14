import React, { useState } from 'react';
import { StyleSheet, Text, View, Button, ScrollView, ActivityIndicator } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import axios from 'axios';

// IMPORTANT: Replace this with your computer's IP address when running on a physical device,
// or use 'http://10.0.2.2:8000' for Android Emulator.
// For local iOS simulator, 'http://127.0.0.1:8000' works.
const API_URL = 'http://127.0.0.1:8000';

export default function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'],
        copyToCacheDirectory: true,
      });
      
      // Checking both Expo SDK 49+ format (result.assets) and older format
      if (!result.canceled && result.assets && result.assets.length > 0) {
        uploadFile(result.assets[0]);
      } else if (result.type === 'success') {
        uploadFile(result);
      }
    } catch (err) {
      console.log('Error picking document', err);
    }
  };

  const uploadFile = async (file) => {
    setLoading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append('file', {
      uri: file.uri,
      name: file.name,
      type: file.mimeType || 'application/octet-stream',
    });
    formData.append('text_column', 'Review Text');

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred during upload.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Review Analyzer ⭐️</Text>
      
      <Button title="Select CSV/Excel File" onPress={pickDocument} disabled={loading} />
      
      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0000ff" />
          <Text>Analyzing reviews...</Text>
        </View>
      )}

      {error && (
        <Text style={styles.errorText}>Error: {error}</Text>
      )}

      {results && (
        <ScrollView style={styles.resultsContainer}>
          <Text style={styles.sectionTitle}>🤖 AI Summary</Text>
          <Text style={styles.summaryText}>{results.ai_summary || "No summary available."}</Text>
          
          <Text style={styles.sectionTitle}>Top Keywords</Text>
          <Text>{results.keywords?.join(', ')}</Text>
          
          <Text style={styles.sectionTitle}>Common Phrases</Text>
          <Text>{results.ngrams?.join(', ')}</Text>

          <Text style={styles.sectionTitle}>Sentiment Distribution</Text>
          {results.sentiment_distribution && Object.entries(results.sentiment_distribution).map(([key, value]) => (
            <Text key={key}>{key}: {value}</Text>
          ))}
          
          <View style={{height: 50}} />
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  loadingContainer: {
    marginTop: 20,
    alignItems: 'center',
  },
  resultsContainer: {
    marginTop: 20,
    flex: 1,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 5,
  },
  summaryText: {
    backgroundColor: '#f0f0f0',
    padding: 10,
    borderRadius: 8,
  },
  errorText: {
    color: 'red',
    marginTop: 10,
  }
});
