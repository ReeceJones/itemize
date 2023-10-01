'use client'
import { Title, Alert, Space } from "@mantine/core";
import PageContainer from "@/components/pagecontainer";
import ItemizeCard from "@/components/itemizecard";
import { useEffect, useState } from "react";
import { Itemize, listUserItemizes } from "@/util/api";


export default function UserPage({ params }: { params: { username: string }}) {
  const [itemizes, setItemizes] = useState<Itemize[] | undefined>(undefined)
  const [listError, setListError] = useState<string | undefined>(undefined)

  async function refreshItemizes() {
    try {
      setItemizes(await listUserItemizes(params.username, ""))
    } catch (error: any) {
      setListError(error.message)
    }
  }

  useEffect(() => {
    refreshItemizes()
  }, [])

  return (
    <PageContainer>
      <Title>{params.username}</Title>
      <Space h={20}/>
      {
        listError && (
          <>
            <Space h={10}/>
            <Alert color="red" title="Error">{listError}</Alert>
          </>
        )
      }
      {
        itemizes && itemizes.map((itemize) => (
          <ItemizeCard key={itemize.slug} itemize={itemize}/>
        ))
      }
    </PageContainer>
  )
}