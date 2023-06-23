<script>
  import { api } from "../main";
  import { content, page } from "../store";
  import { afterUpdate } from "svelte";

  export let upload_date = "";
  export let name = "";
  export let description = "";
  export let imgSrc = "";
  export let dislikes = "";
  export let main_tag = "";
  export let likes = "";
  export let bgSrc = "";
  export let price = 0;
  let card__image;

  afterUpdate(() => {
    if (card__image && bgSrc) {
      card__image.style.backgroundImage = `url(${bgSrc})`;
    }
  });
</script>

<div
  on:keydown={() => {}}
  on:click={async () => {
    content.set(await api.getArticle(main_tag, name));
    page.set("Article");
  }}
  class="card"
>
  <div bind:this={card__image} class="card__image">
    <img src={imgSrc} alt="Loading Gear ..." />
  </div>
  <div class="card__metadata">
    <!-- <div class="card__upload_date">{upload_date}</div> -->
    <div class="card__unit-name">{name}</div>
    <!-- <div class="card__unit-description">{description}</div> -->
    <div class="card__unit-description">{main_tag}</div>
    <div class="card__unit-stats clearfix">
      <div class="stat">
        <div class="stat-label">{price}</div>
        <div class="stat-label-tag">Price</div>
      </div>
    </div>
  </div>
</div>

<style>
  *,
  *:before,
  *:after {
    box-sizing: border-box;
  }

  .card {
    background: var(--ctp-base);
    width: 300px;
    display: inline-block;
    margin: 12px;
    border-radius: 19px;
    position: relative;
    text-align: center;
    box-shadow: -1px 15px 30px -12px black;
    z-index: 9999;
    transition: transform 0.2s ease-in-out;
  }

  .card:hover {
    transform: translateY(-0.25rem);
  }

  .card__image {
    position: relative;
    height: 230px;
    border-top-left-radius: 14px;
    border-top-right-radius: 14px;
    background-repeat: no-repeat;
    background-position: center;
    background-size: 120% 110%;
    box-shadow: inset -1px 5px 50px 20px var(--ctp-base);
  }

  .card__image img {
    width: 48%;
    position: absolute;
    top: -78px;
    left: 75px;
  }

  img:-moz-loading {
    width: 48%;
    height: 40px;
    position: absolute;
    top: 125px;
    left: 80px;
    font-family: "Teko", sans-serif;
    font-size: 20px;
    font-weight: bold;
    color: var(--ctp-sky);
    display: inline-block;
    padding-right: 12px;
    animation: type 0.5s alternate infinite;
  }

  /* img::after { */
  /*   width: 48%; */
  /*   height: 20px; */
  /*   position: absolute; */
  /*   top: 125px; */
  /*   left: 80px; */
  /*   font-family: "Teko", sans-serif; */
  /*   font-size: 20px; */
  /*   font-weight: bold; */
  /*   color: var(--ctp-sky); */
  /*   display: inline-block; */
  /*   padding-right: 12px; */
  /*   animation: type 0.5s alternate infinite; */
  /* } */

  /* .img:not([src]):not([srcset])::after, */
  /* .img[src=""]:not([srcset])::after, */
  /* .img:not(:-moz-loading):not([src]):not([srcset])::after, */
  /* .img:not(:-moz-loading)[src=""]:not([srcset])::after, */
  /* .img:-moz-broken::after { */
  /*   display: flex; */
  /* } */

  /* @keyframes type { */
  /*   from { */
  /*     box-shadow: inset -3px 0px 0px #888; */
  /*   } */
  /*   to { */
  /*     box-shadow: inset -3px 0px 0px transparent; */
  /*   } */
  /* } */

  .card__metadata {
    padding: 10px;
  }

  .card__upload_date {
    text-transform: uppercase;
    font-size: 12px;
    font-weight: 700;
    color: var(--ctp-teal);
  }

  .card__unit-name {
    font-size: 26px;
    color: var(--ctp-text);
    font-weight: 900;
  }

  .card__unit-description {
    font-size: 14px;
    font-weight: bold;
  }

  .card__unit-stats {
    background: var(--ctp-teal);
    color: var(--ctp-subtext2);
    font-weight: 700;
    border-bottom-left-radius: 14px;
    border-bottom-right-radius: 14px;
  }

  .card__unit-stats .stat {
    width: 100%;
    justify-content: center;
    display: flex;
    flex-direction: column;
    /* padding: 20px 15px; */
  }

  .card__unit-stats .stat-value {
    position: relative;
    font-size: 24px;
    margin-bottom: 10px;
  }

  .card__unit-stats .stat-value sup {
    position: absolute;
    bottom: 4px;
    font-size: 45%;
    margin-left: 2px;
  }

  .card__unit-stats .stat-label {
    text-transform: uppercase;
    font-family: "Teko", sans-serif;
    font-size: 42px;
    font-weight: bold;
    color: var(--ctp);
    /* margin-top: 2rem; */
  }

  .card__unit-stats .stat-label-tag {
    text-transform: uppercase;
    font-family: "Teko", sans-serif;
    font-size: 20px;
    font-weight: bold;
    color: var(--ctp);
    margin-bottom: 14px;
    /* margin-top: 2rem; */
  }

  .card__unit-stats .stat:last-child {
    border-right: none;
  }

  .clearfix:after {
    visibility: hidden;
    display: block;
    font-size: 0;
    content: " ";
    clear: both;
    height: 0;
  }
</style>
