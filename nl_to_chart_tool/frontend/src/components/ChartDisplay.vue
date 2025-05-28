<template>
  <div class="chart-display">
    <h3>Chart Will Be Displayed Here</h3>
    <div v-if="chartData" class="chart-container">
      <!-- Placeholder for actual chart rendering -->
      <p>Chart Type: {{ chartData.chart_type }}</p>
      <pre>{{ chartData.data }}</pre>
    </div>
    <div v-else>
      <p>No chart data to display yet. Submit a query to see results.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'; // Added watch

// This prop would be used to pass data from the parent component (App.vue)
const props = defineProps({
  chartData: Object
});

// Use a local ref that reacts to prop changes
const internalChartData = ref(null);

onMounted(() => {
  if (props.chartData) {
    internalChartData.value = props.chartData;
  } else {
    console.log('ChartDisplay mounted, waiting for chartData prop.');
  }
});

// Watch for changes in the chartData prop and update internalChartData
watch(() => props.chartData, (newData) => {
  internalChartData.value = newData;
  console.log('ChartDisplay received new chartData:', newData);
}, { deep: true }); // Use deep watch if chartData is a complex object

</script>

<style scoped>
.chart-display {
  margin-top: 20px;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  background-color: #f9f9f9;
}
.chart-container {
  min-height: 200px; /* Placeholder height */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #fff;
  border: 1px dashed #ccc;
  padding: 10px;
}
pre {
  text-align: left;
  background-color: #efefef;
  padding: 10px;
  border-radius: 4px;
  white-space: pre-wrap; /* Ensure long lines wrap */
  word-break: break-all; /* Ensure long words wrap */
}
</style>
