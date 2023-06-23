import axios from 'axios';
import { getCookieValue, setCookie } from "./shenanigans";

interface ArticleMetadata {
  [key: string]: {
    images?: string[];
    videos?: string[];
    tags?: string[];
    popularity?: number;
    created_at?: string;
    modified_at?: string;
    sentiment?: {
      sentiment_categories?: {
        positive?: string;
        negative?: string;
        neutral?: string;
      };
      sentiment_keywords?: string;
    };
    engagement?: {
      views?: number;
      likes?: number;
      comments?: number;
      shares?: number;
    };
  };
}

class API {
  private baseUrl: string;
  private token: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl + ":80";
    this.token = getCookieValue("token");

    // Bind this to arrow function to access class properties
    axios.interceptors.request.use(
      (config) => {
        config.headers['Authorization'] = `Bearer ${this.token}`;
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );
  }

  async login(username: string, password: string): Promise<boolean> {
    return fetch(`${this.baseUrl}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    })
      .then(async (response) => {
        const data = await response.json();
        if (response.ok) {
          const token = data.token;
          setCookie('token', token);
          this.token = token;
          return true;
        } else {
          throw new Error(data.message);
        }
      })
      .catch((error) => {
        console.error(error);
        return false;
      });
  }

  async createArticle(
    mainTag: string,
    articleName: string,
  ): Promise<Response> {
    return await axios.put(
      `${this.baseUrl}/articles/${mainTag}/${articleName}`,
    );
  }

  async getArticleMetadata(): Promise<ArticleMetadata> {
    const response = await axios.get(`${this.baseUrl}/metadata`);
    return response.data;
  }

  async getArticle(mainTag: string, articleName: string): Promise<Response> {
    const response = await axios.get(
      `${this.baseUrl}/articles/${mainTag}/${articleName}`
    );
    return response.data;
  }

  async updateArticle(
    mainTag: string,
    articleName: string,
    newContent: string
  ): Promise<void> {
    await axios.patch(
      `${this.baseUrl}/articles/${mainTag}/${articleName}`,
      {
        content: newContent
      }
    );
  }

  async deleteArticle(mainTag: string, articleName: string): Promise<void> {
    await axios.delete(
      `${this.baseUrl}/articles/${mainTag}/${articleName}`
    );
  }

  async uploadMedia(category: string, article: string, mediaType: string, filename: string, file: File): Promise<void> {
    // Create a FormData object to send the file
    const formData = new FormData();
    formData.append('file', file);

    // Make the PUT request to the API endpoint
    await axios.put(`${this.baseUrl}/media/${category}/${article}/${mediaType}/${filename}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }

  async getMedia(mediaName: string): Promise<string> {
    const response = await axios.get(
      `${this.baseUrl}/media/${mediaName}`
    );
    const blob = new Blob([response.data]);
    const objectUrl = URL.createObjectURL(blob);
    return objectUrl;
  }

  async reindexArticles(): Promise<void> {
    try {
      await axios.post(`${this.baseUrl}/reindex`);
    } catch (error) {
      console.error('Error reindexing articles:', error);
    }
  }

  async putArticle(category: string, article: string, payload: object): Promise<void> {
    try {
      await axios.put(`${this.baseUrl}/articles/${category}/${article}`, payload);
    } catch (error) {
      console.error('Error putting article:', error);
    }
  }

  async putMedia(category: string, article: string, mediaType: string, filename: string, file: File): Promise<void> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.put(`${this.baseUrl}/media/${category}/${article}/${mediaType}/${filename}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
    } catch (error) {
      console.error('Error uploading media:', error);
    }
  }

  async deleteMedia(media: string): Promise<void> {
    try {
      await axios.delete(`${this.baseUrl}/media/${media}`);
    } catch (error) {
      console.error('Error deleting media:', error);
    }
  }
}

export { API }
