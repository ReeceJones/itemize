'use client'
import { Title, Alert, Space, Box } from "@mantine/core";
import PageContainer from "@/components/pagecontainer";
import ItemizeCard from "@/components/itemizecard";
import { useEffect, useState, useCallback } from "react";
import { Itemize, listUserItemizes } from "@/util/api";


export default function UserPage({ params }: { params: { username: string }}) {
  const [itemizes, setItemizes] = useState<Itemize[] | undefined>(undefined)
  const [listError, setListError] = useState<string | undefined>(undefined)

  const refreshItemizes = useCallback(async function() {
    try {
      setItemizes(await listUserItemizes(params.username, ""))
    } catch (error: any) {
      setListError(error.message)
    }
  }, [params.username])

  useEffect(() => {
    refreshItemizes()
  }, [refreshItemizes])

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
          <Box my={10} key={itemize.slug}>
            <ItemizeCard itemize={itemize}/>
          </Box>
        ))
      }
    </PageContainer>
  )
}