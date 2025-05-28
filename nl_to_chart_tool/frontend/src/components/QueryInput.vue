<template>
  <div class="query-input">
    <textarea v-model="query" placeholder="Enter your natural language query here..."></textarea>
    <button @click="submitQuery">Submit</button>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const query = ref('');

const submitQuery = () => {
  if (query.value.trim() === '') {
    alert('Please enter a query.');
    return;
  }
  // Placeholder for actual submission logic
  console.log('Query submitted:', query.value);
  // Here we would typically emit an event or call a store action
  // For now, we'll just log it and clear the textarea
  alert(`Query to be sent to backend: ${query.value}`);
  query.value = '';
};
</script>

<style scoped>
.query-input {
  margin-bottom: 20px;
}
textarea {
  width: 80%;
  min-height: 80px;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:hover {
  background-color: #369f70;
}
</style>
