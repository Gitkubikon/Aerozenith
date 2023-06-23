<script lang="ts">
  import { api } from "../main";
  import { marked } from "marked";
  import { fade } from "svelte/transition";
  import { createEventDispatcher } from "svelte";
  import { onUltraMount } from "../utils/shenanigans";
  import { writable } from "svelte/store";
  import axios from "axios";

  export let currentArticle;

  let content = "";
  let renderedContent = "";
  let mediaCache = writable({});
  const mediaTypes = ["images", "videos", "cover", "background"];
  const dispatch = createEventDispatcher();
  let sidebarOpen = false;

  function handleClick() {
    dispatch("close-editor");
  }

  function handleVideoError(event) {
    console.error("Video error: ", event);
  }

  async function handleUpload(type: string, file: File) {
    // Uploads and updates the cache
    await api.uploadMedia(
      currentArticle.category,
      currentArticle.article,
      type,
      file.name,
      file
    );
    const url =
      `${window.location.protocol}//${window.location.hostname}` +
      "/media/" +
      file.name;
    mediaCache.update((oldCache) => ({ ...oldCache, [file.name]: url }));
  }

  function handleFileChange(event: Event, type: string) {
    const file = (event.target as HTMLInputElement).files[0];
    handleUpload(type, file);
  }

  function handleChange() {
    let replacedContent = content;
    for (const [filename, url] of Object.entries(mediaCacheValue)) {
      const localPath = `./${filename}`;
      replacedContent = replacedContent.split(localPath).join(url);
    }
    renderedContent = marked(replacedContent);
    api.updateArticle(currentArticle.category, currentArticle.article, content);
  }

  onUltraMount(async () => {
    const response = await api.getArticle(
      currentArticle.category,
      currentArticle.article
    );
    //@ts-ignore
    content = response.content;
    renderedContent = marked(content);

    // Populates the cache
    for (let type of mediaTypes) {
      const metadata = await api.getArticleMetadata();
      const files =
        metadata[currentArticle.category][currentArticle.article][type];
      for (let file of files) {
        const url =
          `${window.location.protocol}//${window.location.hostname}` +
          "/media/" +
          file;
        mediaCache.update((oldCache) => ({ ...oldCache, [file]: url }));
      }
    }
  });

  // Extract the value from the writable store
  let mediaCacheValue;
  mediaCache.subscribe((value) => {
    mediaCacheValue = value;
  });

  // Handle drag and drop inside the textarea
function handleDrop(event: DragEvent) {
  event.preventDefault();
  const path = event.dataTransfer.getData("text/plain");
  const position = event.target.selectionStart;
  const extension = path.split('.').pop().toLowerCase();
  let newContent;
  
  if (extension === "mp4") {
    newContent =
      content.slice(0, position) +
      `<video src="${path}" controls></video>` +
      content.slice(position);
  } else {
    newContent =
      content.slice(0, position) +
      `![${path}](${path})` +
      content.slice(position);
  }
  
  content = newContent;
  handleChange();
}


function handleDragOver(event: DragEvent) {
  event.preventDefault();
  event.dataTransfer.dropEffect = 'copy';
}

</script>

<div class="editor">
  <div class="sidebar" class:open>
    <div class="sidebar-header">
      <div class="toggle-btn" on:click={() => (sidebarOpen = !sidebarOpen)}>
        {#if sidebarOpen}
          <svg fill="var(--ctp-base)" viewBox="0 0 24 24" stroke-width="1.5">
            <path
              stroke="var(--ctp-base)"
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        {:else}
          <svg fill="var(--ctp-base)" viewBox="0 0 24 24" stroke-width="1.5">
            <path
              stroke="var(--ctp-base)"
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M4 6h16M4 12h16m-7 6h7"
            />
          </svg>
        {/if}
      </div>
      <h3>Upload Files</h3>
    </div>
    <div class="upload-menu">
      <label for="image">
        Image
        <input
          type="file"
          id="image"
          name="image"
          accept=".png, .jpg, .jpeg"
          on:change={(e) => handleFileChange(e, "images")}
        />
      </label>

      <label for="video">
        Video
        <input
          type="file"
          id="video"
          name="video"
          accept=".mp4"
          on:change={(e) => handleFileChange(e, "videos")}
        />
      </label>

      <label for="background">
        Background
        <input
          type="file"
          id="background"
          name="background"
          accept=".png, .jpg, .jpeg"
          on:change={(e) => handleFileChange(e, "background")}
        />
      </label>

      <label for="cover">
        Cover
        <input
          type="file"
          id="cover"
          name="cover"
          accept=".png, .jpg, .jpeg"
          on:change={(e) => handleFileChange(e, "cover")}
        />
      </label>
    </div>
    <div class="sidebar-content">
      <div class="uploaded-files">
        {#each Object.entries(mediaCacheValue) as [filename, url] (filename)}
          <div>
            {#if filename.endsWith(".png") || filename.endsWith(".jpg") || filename.endsWith(".jpeg")}
              <img
                src={url}
                alt={filename}
                style="width: 200px;"
              />
            {:else if filename.endsWith(".mp4")}
              <video
                src={url}
                on:error={handleVideoError}
                autoplay
                draggable="true"
                loop
                style="width: 200px;"
              />
            {/if}
          </div>
        {/each}
      </div>
    </div>
  </div>

  <div class="main-content">
    <div
      style="width: 24px;"
      class="close-btn ultrafocus button"
      on:click={handleClick}
    >
      <svg fill="var(--ctp-base)" viewBox="0 0 24 24" stroke-width="1.5">
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke="var(--ctp-red)"
          stroke-linecap="round"
          stroke-linejoin="round"
          fill="var(--ctp-red)"
        />
        <path
          stroke="var(--ctp-red)"
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5"
        />
      </svg>
    </div>
    <div class="markdown-editor">
      <textarea
        class="markdown-textarea"
        bind:value={content}
        on:input={handleChange}
        on:drop|preventDefault={handleDrop}
        on:dragover|preventDefault={handleDragOver}
        placeholder="Write your article here"
      />
    </div>
    <div style="width: 3px; background-color: var(--ctp-crust);" />
    <div class="markdown-preview" transition:fade>
      {@html renderedContent || ""}
    </div>
  </div>
</div>

<style>
  .editor {
    display: flex;
    height: 100%;
    color: var(--ctp-sky);
    background-color: var(--ctp-mantle);
    overflow: hidden;
  }

  .sidebar {
    width: 200px;
    flex-shrink: 0;
    background-color: var(--ctp-base);
    transition: transform 0.2s;
    overflow-y: auto;
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar-header {
    display: flex;
    align-items: center;
    padding: 10px;
    border-bottom: 1px solid var(--ctp-base-dark);
  }

  .toggle-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    margin-right: 10px;
    cursor: pointer;
  }

  .upload-menu {
    padding: 10px;
  }

  .uploaded-files {
    display: flex;
    flex-wrap: wrap;
    padding: 10px;
  }

  .uploaded-files div {
    margin-right: 10px;
    margin-bottom: 10px;
  }

  .uploaded-files img,
  .uploaded-files video {
    max-width: 100px;
    max-height: 100px;
    object-fit: cover;
    cursor: pointer;
  }

  .main-content {
    flex: 1;
    position: relative;
    flex-direction: row;
    display: flex;
  }

  .close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    border: none;
    cursor: pointer;
    transition: transform 0.2s;
  }

  .close-btn:hover {
    transform: scale(1.2);
  }

  .close-btn img {
    width: 20px;
    height: 20px;
  }

  .markdown-editor {
    flex: 1;
    padding: 20px;
  }

  .markdown-textarea {
    display: block;
    width: 100%;
    height: 100%;
    border: none;
    font-size: 16px;
    font-family: "Montserrat", sans-serif;
    resize: none;
    background-color: transparent;
    color: var(--ctp-sky);
    outline: none;
  }

  .markdown-preview {
    flex: 1;
    padding: 20px;
    overflow: auto;
  }
</style>
