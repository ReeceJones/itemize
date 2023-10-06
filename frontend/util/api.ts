import { env } from "next-runtime-env"
import { createContext } from "react"

const API_SERVER = env('NEXT_PUBLIC_BACKEND_URL')

export interface User {
    username: string
    email: string
    first_name: string
    last_name: string
    itemizes: Itemize[] | null
}

export interface MetadataImage {
    source_image_url: string
    url: string
}

export interface PageMetadata {
    url: string
    image_url: string | null
    title: string | null
    description: string | null
    site_name: string | null
    price: string | null
    currency: string | null
    image_id: number | null
    image: MetadataImage | null
}

export interface PageMetadataOverride {
    image_url: string | null
    title: string | null
    description: string | null
    site_name: string | null
    price: string | null
    currency: string | null
}

export interface Link {
    id: number
    url: string
    itemize_id: number
    page_metadata_id: number
    page_metadata_override_id: number | null
    page_metadata: PageMetadata | null
    page_metadata_override: PageMetadataOverride | null
    itemize: Itemize | null
}

export interface Itemize {
    name: string
    slug: string
    description: string | null
    user_id: number
    user: User | null
    links: Link[]
}

interface ItemizeContextHook {
    itemize: Itemize
    setItemize: (itemize: Itemize) => void
    refreshItemize: () => void
}

export const ItemizeContext = createContext<ItemizeContextHook>({
    itemize: {
        name: '',
        slug: '',
        description: '',
        user_id: 0,
        user: null,
        links: [],
    },
    setItemize: () => {},
    refreshItemize: () => {},
})


export async function usernameOrEmailExists(username_or_email: string): Promise<boolean> {
    try {
        const response = await fetch(`${API_SERVER}/users/check/${encodeURIComponent(username_or_email)}`, {
            method: 'GET',
        })
        return response.status == 409
    } catch (e) {
        return true
    }
}


export async function signup(username: string, password: string, email: string, first_name: string, last_name: string) {
    const response = await fetch(`${API_SERVER}/users`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password, email, first_name, last_name }),
    })
    if (response.status != 200) {
        const j = await response.json()
        throw new Error(j['detail'])
    }
    const j = await response.json()
    const access_token = j['token']
    const user: User = j['user']
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('username', user.username)
    localStorage.setItem('auth_header', `Bearer ${access_token}`)
}

export async function login(username: string, password: string) {
    const response = await fetch(`${API_SERVER}/users/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ username, password }),
    })
    if (response.status != 200) {
        const j = await response.json()
        throw new Error(j['detail'])
    }
    const access_token = (await response.json())['access_token']
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('username', username)
    localStorage.setItem('auth_header', `Bearer ${access_token}`)
}

export async function listUserItemizes(username: string, query: string): Promise<Itemize[]> {
    let searchParams: any = {}
    if (query !== null) {
        searchParams.query = query
    }
    const response = await fetch(`${API_SERVER}/itemize/${username}?` + new URLSearchParams(searchParams), {
        method: 'GET',
        headers: {
            'Authorization': localStorage.getItem('auth_header') || '',
        },
    })
    if (response.status != 200) {
        const j = await response.json()
        throw new Error(j['detail'])
    }
    return (await response.json())['itemizes']
}

export async function createItemize(username: string, name: string, description: string | null): Promise<Itemize> {
    const response = await fetch(`${API_SERVER}/itemize/${username}`, {
        method: 'POST',
        headers: {
            'Authorization': localStorage.getItem('auth_header') || '',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, description }),
    })
    if (response.status != 200) {
        const j = await response.json()
        throw new Error(j['detail'])
    }
    return (await response.json())['itemize']
}

export async function getItemize(username: string, slug: string, query: string | null): Promise<Itemize> {
    let searchParams: any = {}
    if (query !== null) {
        searchParams.query = query
    }
    const response = await fetch(`${API_SERVER}/itemize/${username}/${slug}?` + new URLSearchParams(searchParams), {
        method: 'GET',
        headers: {
            'Authorization': localStorage.getItem('auth_header') || '',
        },
        
    })
    if (response.status != 200) {
        const j = await response.json()
        throw new Error(j['detail'])
    }
    return (await response.json())['itemize']
}

export async function addLinkToItemize(username: string, slug: string, url: string): Promise<Link> {
    const response = await fetch(`${API_SERVER}/itemize/${username}/${slug}`, {
        method: 'POST',
        headers: {
            'Authorization': localStorage.getItem('auth_header') || '',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
    })
    const j = await response.json()
    if (response.status != 200) {
        throw new Error(`Failed to add link: ${j['detail']}`)
    }
    return j['link']
}

export async function deleteLinkFromItemize(username: string, slug: string, link_id: number): Promise<void> {
    const response = await fetch(`${API_SERVER}/itemize/${username}/${slug}/${link_id}`, {
        method: 'DELETE',
        headers: {
            'Authorization': localStorage.getItem('auth_header') || '',
        },
    })
    if (response.status != 200) {
        const j = await response.json()
        throw new Error(j['detail'])
    }
}

export async function updateLinkMetadata(username: string, slug: string, link_id: number, metadata_override: PageMetadataOverride): Promise<Link> {
    const response = await fetch(`${API_SERVER}/itemize/${username}/${slug}/${link_id}`, {
        method: 'PATCH',
        headers: {
            'Authorization': localStorage.getItem('auth_header') || '',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(metadata_override),
    })
    if (response.status != 200) {
        const j = await response.json()
        throw new Error(j['detail'])
    }
    return (await response.json())['link']
}
