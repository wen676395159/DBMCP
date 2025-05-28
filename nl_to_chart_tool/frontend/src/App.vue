<template>
  <div id="app">
    <h1>Natural Language to Chart</h1>
    <QueryInput @submit-query="handleQuery" />
    <ChartDisplay :chart-data="currentChartData" />
    <!-- Remove HelloWorld if it's still there and not needed -->
  </div>
</template>

<script setup>
import { ref } from 'vue';
import QueryInput from './components/QueryInput.vue';
import ChartDisplay from './components/ChartDisplay.vue';
// If HelloWorld.vue was created by default and you want to remove it,
// make sure it's not imported or used.

const currentChartData = ref(null);

const handleQuery = async (queryText) => {
  // This is where we will call the backend API
  console.log('App.vue received query:', queryText);
  // Simulate API call and response for now
  // In a real scenario, this would involve:
  // 1. Setting a loading state
  // 2. Making an async call to the backend (e.g., using fetch or axios)
  // 3. Handling success: updating currentChartData.value with the response
  // 4. Handling errors: showing an error message

  // Mock backend call
  alert(`Simulating backend call for: ${queryText}`);
  // Example of what the backend might return (matching ChartDataResponse from backend)
  const mockApiResponse = {
    chart_type: "bar",
    data: {
      labels: ["Category A", "Category B", "Category C"],
      values: [Math.random() * 100, Math.random() * 100, Math.random() * 100]
    }
  };

  // Simulate a delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  currentChartData.value = mockApiResponse;
  console.log('Mock chart data updated:', currentChartData.value);
};
</script>

<style>
/* Keep existing styles or update as needed */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  padding: 20px;
}
</style>
