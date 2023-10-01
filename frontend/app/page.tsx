'use client'
import {TextInput, Textarea, Button, Modal, Box, Center, Space, Alert, Text, Group, Grid, GridCol} from "@mantine/core"
import { useForm } from "@mantine/form";
import { useDisclosure } from "@mantine/hooks";
import { IconSearch } from "@tabler/icons-react";
import PageContainer from "@/components/pagecontainer";
import ItemizeCard from "@/components/itemizecard";
import { listUserItemizes, createItemize, Itemize } from "@/util/api";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const [itemizes, setItemizes] = useState<Itemize[] | undefined>(undefined)
  const [listError, setListError] = useState<string | undefined>(undefined)
  const [opened, { open, close }] = useDisclosure(false)
  const [createLoading, setCreateLoading] = useState<boolean>(false)
  const [createError, setCreateError] = useState<string | undefined>(undefined)
  const {push} = useRouter()
  const createItemizeForm = useForm({
    initialValues: {
      name: "",
      description: ""
    },
    validate: {
      name: (value) => {
        if (value.length < 1) {
          return "Name cannot be empty"
        }
      }
    }
  })
  const queryForm = useForm({
    initialValues: {
      query: "",
    },
  })

  async function refreshItemizes() {
    const username = localStorage.getItem('username')
    if (username === null) {
      setListError("Not logged in")
      return
    }
    try {
      setItemizes(await listUserItemizes(username, queryForm.values['query']))
    } catch (error: any) {
      setListError(error.message)
    }
  }

  async function performCreateItemize() {
    setCreateLoading(true)
    const username = localStorage.getItem('username')
    if (username === null) {
      setCreateError("Not logged in")
      return
    }

    const description = createItemizeForm.values['description'].length > 0 ? createItemizeForm.values['description'] : null

    try {
      const itemize = await createItemize(username, createItemizeForm.values['name'], description)
      push(`/${username}/${itemize.slug}`)
    } catch (error: any) {
      setCreateError(error.message)
      setCreateLoading(false)
      return
    }

    setCreateLoading(false)
  }

  useEffect(() => {
    const username = localStorage.getItem('username')
    if (username === null) {
      setListError("Not logged in")
      return
    }
    refreshItemizes()
  }, [])

  return (
    <PageContainer>
      <Grid>
        <GridCol span={10}>
          <TextInput placeholder="Search" rightSection={<IconSearch size={20}/>} onKeyUp={refreshItemizes} {...queryForm.getInputProps('query')}/>
        </GridCol>
        <GridCol span={2}>
          <Button color="blue" w="100%" onClick={open}>Create Itemize</Button>
          <Modal opened={opened} onClose={close} title="Create Itemize">
            <form onSubmit={createItemizeForm.onSubmit(() => performCreateItemize())}>
              <TextInput label="Name" withAsterisk placeholder="Enter a name for your itemize" {...createItemizeForm.getInputProps('name')}/>
              <Textarea label="Description" placeholder="Enter a description for your itemize" {...createItemizeForm.getInputProps('description')}/>
              <Space h={10}/>
              <Button fullWidth type="submit" loading={createLoading} onClick={performCreateItemize}>Create Itemize</Button>
              {
                createError && (
                  <>
                    <Space h={10}/>
                    <Alert color="red" title="Error">{createError}</Alert>
                  </>
                )
              }
            </form>
          </Modal>
        </GridCol>
      </Grid>
      <Space h={20}/>
      {
        listError && (
          <Alert color="red" title="Error">{listError}</Alert>
        )
      }
      {
        itemizes && (
          itemizes.length === 0 ? (
            <Alert color="gray">
              <Text size="lg">You have no itemizes, create one to get started.</Text>
            </Alert>
          )
          : itemizes?.map((itemize) => (<ItemizeCard itemize={itemize}/>))
        )
      }
    </PageContainer>
  )
}