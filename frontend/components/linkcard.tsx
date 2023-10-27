'use client'
import { Card, Image, Text, Stack, UnstyledButton, AspectRatio, Grid, GridCol, Button, Space, Flex, ActionIcon, Popover, PopoverTarget, PopoverDropdown, Alert, Modal, TextInput, NumberInput, Select, Box } from "@mantine/core"
import { useHover, useDisclosure } from "@mantine/hooks"
import { useForm } from "@mantine/form"
import Link from "next/link"
import { Link as ILink, ItemizeContext, deleteLinkFromItemize, updateLinkMetadata } from "@/util/api"
import { IconDotsVertical } from "@tabler/icons-react"
import { useState, useContext } from "react"


function getActiveValue(base: string | null | undefined, override: string | null | undefined): string {
  if (override !== null && override !== undefined) {
    return override
  }
  if (base !== null && base !== undefined) {
    return base
  }
  return ''
}

function getCurrencySymbol(currency: string | null | undefined): string {
  if (currency === 'USD') {
    return '$'
  }
  return ''
}


export default function LinkCard({link}: { link: ILink }) {
  const {hovered, ref} = useHover()
  const [linkDisabled, setLinkDisabled] = useState<boolean>(false)
  const [deleteLoading, setDeleteLoading] = useState<boolean>(false)
  const [deleteError, setDeleteError] = useState<string | undefined>(undefined)
  const [editLoading, setEditLoading] = useState<boolean>(false)
  const [editError, setEditError] = useState<string | undefined>(undefined)
  const [popoverOpen, setPopoverOpen] = useState<boolean>(false)
  const {itemize, refreshItemize} = useContext(ItemizeContext)
  const [opened, {open, close}] = useDisclosure(false)

  const url = link.url
  const title = getActiveValue(link.page_metadata?.title, link.page_metadata_override?.title)
  const description = getActiveValue(link.page_metadata?.description, link.page_metadata_override?.description)
  const site_name = getActiveValue(link.page_metadata?.site_name, link.page_metadata_override?.site_name)
  const price = getActiveValue(link.page_metadata?.price, link.page_metadata_override?.price)
  const currency = getActiveValue(link.page_metadata?.currency, link.page_metadata_override?.currency)

  const form = useForm({
    initialValues: {
      title: title,
      description: description,
      site_name: site_name,
      price: price,
      currency: currency,
    }
  })

  async function deleteLink() {
    setDeleteLoading(true)
    const username = itemize.user?.username
    if (username === undefined) {
      setDeleteError("Error parsing link data: could not get username")
      setDeleteLoading(false)
      return
    }
    try {
      await deleteLinkFromItemize(username, itemize.slug, link.id)
    } catch (error: any) {
      setDeleteError(error.message)
      setDeleteLoading(false)
      return
    }
    try {
      refreshItemize()
    } catch (error: any) {
      setDeleteError(error.message)
      setDeleteLoading(false)
      return
    }
    setDeleteLoading(false)
  }

  async function updateLink() {
    setEditLoading(true)
    const username = itemize.user?.username
    if (username === undefined) {
      setEditError("Error parsing link data: could not get username")
      setEditLoading(false)
      return
    }
    try {
      await updateLinkMetadata(username, itemize.slug, link.id, {
        title: form.isDirty('title') ? form.values['title'] : null,
        description: form.isDirty('description') ? form.values['description'] : null,
        site_name: form.isDirty('site_name') ? form.values['site_name'] : null,
        price: form.isDirty('price') ? form.values['price'].toString() : null,
        currency: form.isDirty('currency') ? form.values['currency'] : null,
        image_url: null,
      })
    } catch (error: any) {
      setEditError(error.message)
      setEditLoading(false)
      return
    }
    try {
      refreshItemize()
    } catch (error: any) {
      setEditError(error.message)
      setEditLoading(false)
      return
    }
    setEditLoading(false)
    close()
  }

  async function openModal() {
    setPopoverOpen(false)
    open()
  }

  return (
    <>
      <UnstyledButton w="100%" component={Link} href={url} key={link.id} onClick={(e) => {
        if (hovered || linkDisabled || opened) {
          e.preventDefault()
          e.stopPropagation()
        }
      }}>
        <Card shadow="sm" padding={0} radius="md" withBorder>
          <Grid>
            <GridCol span={2}>
              <AspectRatio ratio={1} mih={150}>
                {
                  link.page_metadata?.image?.url ? (
                    <Image src={link.page_metadata?.image?.url} alt={description}></Image>
                  ) : (
                    <Box h={150} bg="gray.2"/>
                  )
                }
              </AspectRatio>
            </GridCol>

            <GridCol span={10}>
              <Stack my={10}>
                <Grid>
                  <GridCol span={11}>
                    <Text fw={500} lineClamp={1}>{
                      site_name && (
                        <Text component="span" c="dimmed">{site_name}</Text>
                      )
                    } {title || url}
                    </Text>
                  </GridCol>
                  <GridCol span={1}>
                    <Flex justify="flex-end" mx={10}>
                      <div ref={ref}>
                        <Popover width={200} opened={popoverOpen} onChange={setPopoverOpen} onOpen={() => setLinkDisabled(true)} onClose={() => setLinkDisabled(false)}>
                          <PopoverTarget>
                            <ActionIcon variant="subtle" color="dark" onClick={() => setPopoverOpen(true)}><IconDotsVertical size={18}/></ActionIcon>
                          </PopoverTarget>
                          <PopoverDropdown>
                            <Button fullWidth onClick={openModal}>Edit</Button>
                            <Space h={10}/>
                            <Button color="red" loading={deleteLoading} onClick={deleteLink} fullWidth>Delete</Button>
                            {
                              deleteError && (
                                <>
                                  <Space h={10}/>
                                  <Alert color="red" title="Error">{deleteError}</Alert>
                                </>
                              )
                            }
                          </PopoverDropdown>
                        </Popover>
                      </div>
                    </Flex>
                  </GridCol>
                </Grid>
                <Text size="sm" c="dimmed" lineClamp={2}>{description}</Text>
                {
                  price && (
                    <Text c="dimmed">{parseFloat(price).toLocaleString("en-US", {style: "currency", currency: currency || "USD"})}</Text>
                  )
                }
              </Stack>
            </GridCol>
          </Grid>
        </Card>
      </UnstyledButton>
      <Modal title="Edit Link" opened={opened} onClose={close}>
        <Image src={link.page_metadata?.image?.url} alt={description}></Image>
        <Space h={10}/>
        {/* <FileButton onChange={setCustomImage} accept="image/png,image/jpeg">
          {(props) => <Button {...props} fullWidth><IconFileUpload size={18}/> Upload Image</Button>}
        </FileButton> */}
        <Space h={10}/>
        <form onSubmit={form.onSubmit(updateLink)}>
          <TextInput label="URL" placeholder="url" disabled value={url}/>
          <TextInput label="Title" placeholder="title" {...form.getInputProps('title')}/>
          <TextInput label="Description" placeholder="description" {...form.getInputProps('description')}/>
          <TextInput label="Site Name" placeholder="site name" {...form.getInputProps('site_name')}/>
          <NumberInput thousandSeparator="," decimalScale={2} label="Price" placeholder="price" hideControls {...form.getInputProps('price')}/>
          <Select data={[{value: 'USD', label: 'USD ($)'}]} label="Currency" placeholder="currency" {...form.getInputProps('currency')}/>
          {
            editError && (
              <>
                <Space h={10}/>
                <Alert color="red" title="Error">{editError}</Alert>
              </>
            )
          }
          <Space h={10}/>
          <Button type="submit" loading={editLoading} fullWidth>Save</Button>
        </form>
      </Modal>
    </>
  )
}