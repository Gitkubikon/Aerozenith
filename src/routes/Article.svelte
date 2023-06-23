<script>
  import { fade, fly } from "svelte/transition";
  import { onMount } from "svelte";
  import { content } from "../store";
  import { marked } from "marked";
  import { createPayment, getPaymentMethods } from "../api/payment"; // Import your payment-related functions from an API module

  let paymentMethods = [];

  onMount(async () => {
    // Fetch available payment methods
    paymentMethods = await getPaymentMethods();
  });

  async function handlePayment(method) {
    // Handle the payment logic based on the selected payment method
    const paymentResult = await createPayment(method);
    console.log("Payment Result:", paymentResult);
    // Add any additional logic or UI updates after payment is processed
  }
</script>

<section transition:fly={{ y: 1000 }}>
  <article>
    {@html marked($content.content)}
  </article>

  <div>
    <h3>Payment Options</h3>
    <ul>
      {#each paymentMethods as method}
        <li on:click={() => handlePayment(method)}>{method}</li>
      {/each}
    </ul>
  </div>

  <style>
    article {
      font-family: sans-serif;
      line-height: 1.5;
      font-size: 16px;
      font-family: "Montserrat", sans-serif;
      resize: none;
      background-color: transparent;
      color: var(--ctp);
      padding-bottom: 80px;
    }
    div {
      margin-top: 40px;
    }
    h3 {
      font-size: 18px;
      margin-bottom: 10px;
    }
    ul {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    li {
      cursor: pointer;
      padding: 5px;
      margin-bottom: 5px;
      background-color: lightgray;
      border-radius: 4px;
    }
    li:hover {
      background-color: gray;
      color: white;
    }
  </style>
</section>

