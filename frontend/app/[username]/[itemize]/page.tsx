'use client'
import { Modal, Button, Alert, Space, Text, Group, ActionIcon, TextInput, Textarea, Box, Breadcrumbs, Anchor, Skeleton, Popover, PopoverTarget, PopoverDropdown, Pill, Switch } from "@mantine/core"
import { useDisclosure } from "@mantine/hooks"
import { useForm } from "@mantine/form"
import LinkCard from "@/components/linkcard"
import { useEffect, useState, useCallback } from "react"
import { getItemize, Itemize, ItemizeContext } from "@/util/api"
import { IconSearch, IconPlus, IconAdjustmentsHorizontal } from "@tabler/icons-react"
import Link from "next/link"
import { addLinkToItemize, updateItemize } from "@/util/api"
import PageContainer from "@/components/pagecontainer"
import { useRouter } from "next/navigation"


export default function Home({ params }: { params: { username: string, itemize: string } }) {
  const [itemize, setItemize] = useState<Itemize | undefined>(undefined)
  const [addLoading, setAddLoading] = useState<boolean>(false)
  const [updateLoading, setUpdateLoading] = useState<boolean>(false)
  const [opened, { open, close }] = useDisclosure(false)
  const [listError, setListError] = useState<string | undefined>(undefined)
  const [addError, setAddError] = useState<string | undefined>(undefined)
  const [updateError, setUpdateError] = useState<string | undefined>(undefined)
  const { push } = useRouter()

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
  const settingsForm = useForm({
    initialValues: {
      name: '',
      description: '',
      public: false,
    }
  })

  const refreshItemize = useCallback(async function() {
    const newItemize = await getItemize(params.username, params.itemize, queryForm.values['query'])
    setItemize(newItemize)
    const newValues = {
      name: newItemize.name,
      description: newItemize.description || '',
      public: newItemize.public,
    }
    settingsForm.setInitialValues(newValues)
    settingsForm.setValues(newValues)
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

  async function performItemizeUpdate() {
    setUpdateLoading(true)
    const values = {
      name: settingsForm.isDirty('name') ? settingsForm.values['name'] : null,
      description: settingsForm.isDirty('description') ? settingsForm.values['description'] : null,
      public: settingsForm.isDirty('public') ? settingsForm.values['public'] : null,
    }
    try {
      const newItemize = await updateItemize(params.username, params.itemize, values)
      setUpdateError(undefined)
      if (newItemize.slug != params.itemize) {
        push(`/${params.username}/${newItemize.slug}`) 
        return
      }
      try {
        await refreshItemize()
      } catch (error: any) {
        setListError(error.message)
      }
      setUpdateLoading(false)
    } catch (error: any) {
      console.log(error)
      setUpdateError(error.message)
      setUpdateLoading(false)
    }
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
        <Group justify="space-between">
          <Group>
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
              itemize?.public === false && (
                <Pill>Private</Pill>
              )
            }
          </Group>

          <Popover>
            <PopoverTarget>
              <ActionIcon variant="subtle" color="dark"><IconAdjustmentsHorizontal size={20}/></ActionIcon>
            </PopoverTarget>
            <PopoverDropdown>
              <form onSubmit={settingsForm.onSubmit(performItemizeUpdate)}>
                <TextInput label="Name" placeholder="Name" {...settingsForm.getInputProps('name')}/>
                <Space h={10}/>
                <Textarea label="Description" placeholder="Description" {...settingsForm.getInputProps('description')}/>
                <Space h={10}/>
                <Switch label="Public" defaultChecked={settingsForm.values['public']} {...settingsForm.getInputProps('public')} />
                {
                  updateError && (
                    <>
                      <Space h={10}/>
                      <Alert color="red" title="Error">{updateError}</Alert>
                    </>
                  )
                }
                <Space h={10}/>
                <Button type="submit" loading={updateLoading} fullWidth>Save</Button>
              </form>
            </PopoverDropdown>
          </Popover>
        </Group>
        {
          itemize?.description && (
            <>
              <Space h={10}/>
              <Text size="md" c="dark" fw={300}>{itemize?.description}</Text>
            </>
          )
        }
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
