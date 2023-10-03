'use client'
import { Modal, Button, Alert, Space, Text, Title, TextInput, Box, Breadcrumbs, Anchor, Skeleton } from "@mantine/core"
import { useDisclosure } from "@mantine/hooks"
import { useForm } from "@mantine/form"
import LinkCard from "@/components/linkcard"
import { useEffect, useState, useCallback } from "react"
import { getItemize, Itemize, ItemizeContext } from "@/util/api"
import { IconSearch, IconPlus } from "@tabler/icons-react"
import Link from "next/link"
import { addLinkToItemize } from "@/util/api"
import PageContainer from "@/components/pagecontainer"


export default function Home({ params }: { params: { username: string, itemize: string } }) {
  const [itemize, setItemize] = useState<Itemize | undefined>(undefined)
  const [addLoading, setAddLoading] = useState<boolean>(false)
  const [opened, { open, close }] = useDisclosure(false)
  const [listError, setListError] = useState<string | undefined>(undefined)
  const [addError, setAddError] = useState<string | undefined>(undefined)

  const addLinkForm = useForm({
    initialValues: {
      url: "",
    },
    validate: {
      url: (value) => {
        if (value.length < 1) {
          return "URL cannot be empty"
        }
        if (value.search(/^https?:\/\//) === -1) {
          return "URL must start with http:// or https://"
        }
      }
    }
  })
  const queryForm = useForm({
    initialValues: {
      query: "",
    },
  })

  const refreshItemize = useCallback(async function() {
    setItemize(await getItemize(params.username, params.itemize, queryForm.values['query']))
  }, [params.username, params.itemize, queryForm.values])

  async function performLinkAdd() {
    if (itemize === undefined) {
      setAddError("Itemize is undefined")
      return
    }
    setAddLoading(true)
    const url = addLinkForm.values['url']
    try {
      await addLinkToItemize(params.username, itemize.slug, url)
      addLinkForm.reset()
      setAddError(undefined)
      try {
        await refreshItemize()
      } catch (error: any) {
        setListError(error.message)
      }
      setAddLoading(false)
      close()
    } catch (error: any) {
      console.log(error)
      setAddError(error.message)
      setAddLoading(false)
    }
  }
  
  async function performQuery() {
    await refreshItemize()
  }

  useEffect(() => {
    refreshItemize().then((itemize) => {
      console.log(itemize)
    }).catch((error) => {
      console.log(error)
      setListError(error.message)
    })
  }, [refreshItemize])

  if (listError === undefined) {
    return (
      <PageContainer>
        {
          itemize !== undefined ? (
            <Breadcrumbs>
              <Anchor component={Link} href={`/${params.username}`} size="xl" fw={500}>{params.username}</Anchor>
              <Text size="xl" fw={500}>{itemize.name}</Text>
            </Breadcrumbs>
          ) : (
            <Breadcrumbs>
              <Skeleton width={100} height={20}/>
              <Skeleton width={150} height={20}/>
            </Breadcrumbs>
          )
        }
        {
          itemize?.description && (
            <>
              <Space h={10}/>
              <Text size="md" c="dark" fw={300}>{itemize?.description}</Text>
            </>
          )
        }
        {/* <Link href={`/${itemize?.owner}`}><Text component="span" c="gray" size="lg" td="underline" fw={500}>{itemize?.owner}</Text></Link> */}
        <Space h={20}/>
        <TextInput placeholder="Search" rightSection={<IconSearch size={18}/>} onKeyUp={performQuery} {...queryForm.getInputProps('query')}/>
        <Space h={20}/>
        {
          itemize && (
            <ItemizeContext.Provider value={{itemize, setItemize, refreshItemize}}>
              {
                (itemize.links.length === 0 && !queryForm.isDirty()) ? (
                  <Alert color="gray">
                    <Text size="md">No links have been added yet...</Text>
                  </Alert>
                ) : itemize.links.map((link) => 
                <Box my={10} key={link.id}>
                  <LinkCard link={link}/>
                </Box>)
              }
            </ItemizeContext.Provider>
          )
        }
        <Space h={20}/>
        <Button fullWidth variant="light" color="dark" size="md" onClick={open}>
          <IconPlus size={24} color="gray"/>
        </Button>
        <Modal opened={opened} onClose={close} centered title="Add link">
          <form onSubmit={addLinkForm.onSubmit(() => performLinkAdd())}>
            <TextInput label="Link URL" placeholder="URL" withAsterisk {...addLinkForm.getInputProps('url')}/>
            <Space h={10}/>
            <Button fullWidth loading={addLoading} type="submit">Add</Button>
            {
              (addError !== undefined) ? (
                <Alert mt={10} color="red" radius="md">
                  {addError}
                </Alert>
              ) : <></>
            }
          </form>
        </Modal>
      </PageContainer>
    )
  } else {
    return (
      <PageContainer>
        <Alert color="red" title="Error">{listError}</Alert>
      </PageContainer>
    )
  }
}
