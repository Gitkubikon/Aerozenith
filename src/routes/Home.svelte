<script lang="ts">
  import { fly, fade } from "svelte/transition";
  import ArticleCard from "../components/ArticleCard.svelte";
  import Footer from "../components/Footer.svelte";
  import { api } from "../main";
  import { onUltraMount } from "../utils/shenanigans";

  let meta = null;
  let categories = [];
  let currentArticle = {};
  let selectedCategory = "";

  let edit = false;
  let currentImage = 0;
  let previousImage = -1;
  let nextImage = 1;
  let images = [
    "001.png",
    "002.png",
    "003.png",
    "004.png",
    "005.png",
    "006.png",
    "007.png",
  ];

  function handleCloseEditor() {
    edit = false;
  }

  onUltraMount(async () => {
    meta = await api.getArticleMetadata();

    // Add imgSrc and bgSrc to metadata
    for (const category of Object.keys(meta)) {
      for (const article of Object.keys(meta[category])) {
        const metadata = meta[category][article];
        metadata.imgSrc = `${window.location.protocol}//${window.location.hostname}/media/${metadata["cover"]}`;
        metadata.bgSrc = `${window.location.protocol}//${window.location.hostname}/media/${metadata["background"]}`;
      }
    }

    categories = Object.keys(meta);
    if (categories.length > 0) {
      selectedCategory = "";
    }

    setInterval(() => {
      previousImage = currentImage;
      currentImage = (currentImage + 1) % images.length;
      nextImage = (currentImage + 1) % images.length;
    }, 8000);
  });
</script>

<section transition:fly={{ y: -1000 }}>
  <div id="carousel">
    {#key currentImage}
      <img
        src={`./Gigapixel/${images[currentImage]}`}
        alt="Banner Image"
        transition:fly={{ x: -1000 }}
      />
    {/key}
  </div>

  <div class="category-cards">
    <div
      on:keydown={() => {}}
      on:click={() => {
        selectedCategory = "";
      }}
      class={selectedCategory === ""
        ? "active ultrafocus button"
        : "ultrafocus button"}
    >
      All
    </div>
    {#each categories as category}
      <div
        on:keydown={() => {}}
        on:click={() => {
          selectedCategory = category;
        }}
        class={selectedCategory === category
          ? "active ultrafocus button"
          : "ultrafocus button"}
      >
        {category}
      </div>
    {/each}
  </div>
  <div class="article-cards">
    {#if meta !== null}
      {#each Object.entries(meta) as [category, articles]}
        {#if (selectedCategory === "" && category !== "legal") || selectedCategory === category}
          {#each Object.entries(articles) as [article, metadata]}
            <div
              on:keydown={() => {}}
              on:click={() => {
                currentArticle = { category, article };
              }}
              class="article"
            >
              <ArticleCard
                upload_date={metadata.created_at}
                name={article}
                description={metadata.description}
                imgSrc={metadata.imgSrc}
                bgSrc={metadata.bgSrc}
                price={metadata.price}
                dislikes="0"
                main_tag={category}
                likes="0"
              />
            </div>
          {/each}
        {/if}
      {/each}
      <div class="intro">
        <p class="intro-text">
          Rev Up Your Style and Safety with Aerozenith [アエロゼニス]
        </p>
        <p class="intro-paragraph">
          Welcome to Aerozenith [アエロゼニス], your destination for exceptional
          motorcycle apparel that combines style and safety. We believe that
          riding a motorcycle is an exhilarating adventure, and your gear should
          match that excitement. With our carefully curated collection of
          high-quality garments, we bring together fashion and functionality in
          perfect harmony.
        </p>

        <p class="intro-paragraph">
          Discover a world where style meets protection. Our garments are
          crafted with precision and feature durable materials like Cordura,
          ensuring that you're geared up for any road condition. Ride with
          confidence, knowing that your clothing can withstand the demands of
          the ride while keeping you comfortable.
        </p>

        <p class="intro-paragraph">
          We understand that being comfortable on your motorcycle is crucial.
          That's why we incorporate moisture-wicking fabrics to keep you dry and
          cool, and breathable textiles to provide optimal airflow. Our gear
          moves with you, offering flexibility and freedom of movement, so you
          can focus on the thrill of the ride.
        </p>

        <p class="intro-paragraph">
          At アエロゼニス, we take pride in offering you more than just apparel.
          We embody a philosophy that celebrates individuality and embraces the
          spirit of the road. Our garments make a statement, reflecting your
          unique style while ensuring your safety remains paramount.
        </p>

        <p class="intro-paragraph">
          Explore our collection and find the perfect gear that speaks to your
          personality and enhances your riding experience. From jackets to
          pants, gloves to helmets, we have everything you need to make your
          mark on the road. Join us in embracing the adventure and ride in style
          with Aerozenith!.
        </p>

        <p class="intro-paragraph">
          Gear up, look sharp, and let the journey begin.
        </p>
      </div>
    {:else}
      <div class="intro">
        <p class="intro-text-loading">Loading Gear...</p>
        <p class="intro-text">
          Rev Up Your Style and Safety with Aerozenith [アエロゼニス]
        </p>
        <p class="intro-paragraph">
          Welcome to アエロゼニス, your destination for exceptional motorcycle
          apparel that combines style and safety. We believe that riding a
          motorcycle is an exhilarating adventure, and your gear should match
          that excitement. With our carefully curated collection of high-quality
          garments, we bring together fashion and functionality in perfect
          harmony.
        </p>

        <p class="intro-paragraph">
          Discover a world where style meets protection. Our garments are
          crafted with precision and feature durable materials like Cordura,
          ensuring that you're geared up for any road condition. Ride with
          confidence, knowing that your clothing can withstand the demands of
          the ride while keeping you comfortable.
        </p>

        <p class="intro-paragraph">
          We understand that being comfortable on your motorcycle is crucial.
          That's why we incorporate moisture-wicking fabrics to keep you dry and
          cool, and breathable textiles to provide optimal airflow. Our gear
          moves with you, offering flexibility and freedom of movement, so you
          can focus on the thrill of the ride.
        </p>

        <p class="intro-paragraph">
          At [Your Business Name], we take pride in offering you more than just
          apparel. We embody a philosophy that celebrates individuality and
          embraces the spirit of the road. Our garments make a statement,
          reflecting your unique style while ensuring your safety remains
          paramount.
        </p>

        <p class="intro-paragraph">
          Explore our collection and find the perfect gear that speaks to your
          personality and enhances your riding experience. From jackets to
          pants, gloves to helmets, we have everything you need to make your
          mark on the road. Join us in embracing the adventure and ride in style
          with アエロゼニス.
        </p>

        <p class="intro-paragraph">
          Gear up, look sharp, and let the journey begin.
        </p>
      </div>
    {/if}
  </div>

  <Footer />
</section>

<style>
  section {
    display: flex;
    flex-wrap: wrap;
    flex-direction: row;
    justify-content: center;
  }

  .intro {
    z-index: 6;
    margin-bottom: 5rem;
  }

  #carousel {
    z-index: 1;
    width: 100vw;
    height: 920px; /* adjust accordingly */
    overflow: hidden;
    position: relative;
    margin-bottom: -700px;
    margin-top: -5rem;
    margin-right: -5rem;
    margin-left: -5rem;
  }

  #carousel::after {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        to bottom,
        rgba(0, 0, 0, 0.1) 0%,
        transparent 10%
      ),
      linear-gradient(to bottom, transparent 0%, var(--ctp-surface1) 72%);
    pointer-events: none;
  }

  #carousel img {
    width: 100%;
    height: auto;
    object-fit: cover;
  }

  .category-cards {
    display: flex;
    justify-content: center;
    margin-bottom: 32px;
    z-index: 2;
  }

  .article-cards {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
    width: 100%;
  }
  .category-cards > div {
    display: flex;
    height: 24px;
    justify-content: center;
    align-content: center;
    font-size: 16px;
    font-weight: bold;
    border-radius: 16px;
    color: var(--ctp-text);
  }

  .category-cards > div.active {
    background-color: var(--ctp) !important;
  }

  .category-cards div {
    /* Set common styles for category cards */
    padding: 10px;
    margin-right: 10px;
    cursor: pointer;
    color: #fff;
    font-weight: bold;
  }
  /* Set background colors using CSS variables */
  .category-cards div:nth-child(1) {
    background-color: var(--ctp-rosewater);
  }
  .category-cards div:nth-child(2) {
    background-color: var(--ctp-flamingo);
  }
  .category-cards div:nth-child(3) {
    background-color: var(--ctp-pink);
  }
  .category-cards div:nth-child(4) {
    background-color: var(--ctp-lavender);
  }
  .category-cards div:nth-child(5) {
    background-color: var(--ctp-red);
  }
  .category-cards div:nth-child(6) {
    background-color: var(--ctp-maroon);
  }
  .category-cards div:nth-child(7) {
    background-color: var(--ctp-peach);
  }
  .category-cards div:nth-child(8) {
    background-color: var(--ctp-yellow);
  }
  .category-cards div:nth-child(9) {
    background-color: var(--ctp-green);
  }
  .category-cards div:nth-child(10) {
    background-color: var(--ctp-teal);
  }
  .category-cards div:nth-child(11) {
    background-color: var(--ctp-sky);
  }
  .category-cards div:nth-child(12) {
    background-color: var(--ctp-sapphire);
  }
  .category-cards div:nth-child(13) {
    background-color: var(--ctp-blue);
  }

  .intro-text {
    font-family: "Teko", sans-serif;
    font-size: 48px;
    font-weight: bold;
    color: var(--ctp-sky);
    margin-top: 2rem;
  }

  .intro-text-loading {
      /* Your styles here */
      /* For example: */

      height: 46px;
      font-family: "Teko", sans-serif;
      font-size: 48px;
      font-weight: bold;
      color: var(--ctp-sky);
      display: inline-block;
      padding-right: 12px;
      animation: type 0.5s alternate infinite;
    }

  .intro-paragraph {
    font-family: "Urbanist", sans-serif;
    font-size: 18px;
    font-weight: 500;
    line-height: 1.5;
    margin: 1rem 0;
    color: var(--ctp-text);
  }

  @keyframes type {
    from {
      color: var(--ctp-subtext1);
    }
    to {
      color: transparent;
    }
  }

  /* Breathing animation */
  @keyframes breathing {
    0% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
    100% {
      opacity: 1;
    }
  }

  .article {
    margin-bottom: 1.5rem;
  }
</style>
